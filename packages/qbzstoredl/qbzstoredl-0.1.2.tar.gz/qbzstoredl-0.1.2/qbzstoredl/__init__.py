#!/usr/bin/python3

import asyncio
import logging
import subprocess
from datetime import datetime
from io import BytesIO
from optparse import OptionParser
from pathlib import Path
from pprint import pformat

import ffpb
import httpx
import mutagen.flac
import mutagen.id3
import mutagen.mp3
import pathvalidate
from PIL import Image
from tqdm import tqdm


class QobuzDownloader:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self._client = httpx.AsyncClient()
        self._client.headers.update({"user-agent": "Dart/3.1 (dart:io)"})
        self._dlqueue = []
        xdg_dl_query = subprocess.run(
            ["xdg-user-dir", "DOWNLOAD"], check=True, capture_output=True, text=True
        )
        self._out_base = Path(xdg_dl_query.stdout.strip()) / "qbzstoredl"

    async def enqueue_download(self, qbzdl_url: str, format: str) -> None:
        self._logger.info(f"Fetching download info from {qbzdl_url}")
        token = self._get_token_from_url(qbzdl_url)
        self._qbzdl_data = await self._get_metadata(token)
        self._logger.debug(f"Download info: {pformat(self._qbzdl_data)}")
        self._albums_by_id = dict(
            (album["id"], album) for album in self._metadata["albums"]
        )
        self._audios_by_track_id = dict(
            (audio["track_id"], audio) for audio in self._qbzdl_data["audios"]
        )

        self._logger.info("Processing download info")
        await asyncio.gather(
            *[self._process_album(a, format=format) for a in self._albums_by_id.keys()]
        )

    async def run(self) -> None:
        self._logger.info("Starting download")
        await self._work_download_queue()
        self._logger.info("Download finished")

    async def _download_file(self, url: str, filename: Path) -> None:
        if filename.exists():
            pass

        with open(filename, "wb") as f:
            async with self._client.stream("GET", url) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))

                tqdm_params = {
                    "desc": str(filename),
                    "total": total,
                    "miniters": 1,
                    "unit": "B",
                    "unit_scale": True,
                    "unit_divisor": 1024,
                }
                with tqdm(**tqdm_params) as pb:
                    downloaded = r.num_bytes_downloaded
                    async for chunk in r.aiter_bytes():
                        pb.update(r.num_bytes_downloaded - downloaded)
                        f.write(chunk)
                        downloaded = r.num_bytes_downloaded

    async def _process_file(self, dl_info: dict) -> None:
        await self._download_file(dl_info["url"], dl_info["filename"])
        if "postprocess" in dl_info:
            await dl_info["postprocess"](dl_info["filename"])

    async def _work_download_queue(self) -> None:
        # Setting this > 1 does not work well currently, needs investigating
        concurrent_limit = 1
        tasks: set[asyncio.Task] = set()
        while self._dlqueue or tasks:
            while self._dlqueue and (len(tasks) < concurrent_limit):
                dl_info = self._dlqueue.pop()
                tasks.add(asyncio.create_task(self._process_file(dl_info)))
            done, _ = await asyncio.wait(tasks, return_when="FIRST_COMPLETED")
            for task in done:
                # Check for exceptions
                await task
            tasks -= done

    @property
    def _metadata(self) -> dict:
        return self._qbzdl_data["metadata"]

    @property
    def _audios(self) -> dict:
        return self._qbzdl_data["audios"]

    def _get_token_from_url(self, qbzdl_url: str) -> str:
        if not qbzdl_url.startswith("qbzdl://"):
            raise ValueError("Download URL does not start with qbzdl://")
        return qbzdl_url[8:]

    async def _get_metadata(self, dltoken: str) -> dict:
        response = await self._client.get(
            f"https://qobuz.com/v4/downloader/info?token%5B%5D={dltoken}",
            follow_redirects=True,
        )
        response.raise_for_status()
        metadata = response.json()
        assert len(metadata) == 1
        return metadata[0]

    async def _fetch_album_cover(self, album: dict) -> None:
        cover_url = album["image"]["large"]
        self._logger.debug(f"Downloading cover from {cover_url}")
        cover_response = await self._client.get(cover_url, follow_redirects=True)
        cover_response.raise_for_status()
        cover_image = Image.open(BytesIO(cover_response.content))
        if cover_image.format != "JPEG":
            raise RuntimeError(
                f"Unknown cover image format {cover_image.format} for album {album['id']}"
            )
        album["_cover"] = dict(image=cover_image, data=cover_response.content)

    async def _process_album(self, album_id: str, format: str) -> None:
        album = self._albums_by_id[album_id]
        self._logger.debug(f"Processing album ID {album_id} / {album['title']}")

        if "image" in album:
            await self._fetch_album_cover(album)

        tracks_in_album = list(
            filter(lambda t: t["album"]["id"] == album_id, self._metadata["tracks"])
        )
        directory = self._out_base / self._sanitize_filename(album["title"])
        Path(directory).mkdir(parents=True, exist_ok=True)
        album_has_multiple_discs = any(t["track_disc"] != 1 for t in tracks_in_album)
        for track in tracks_in_album:
            self._download_track(
                track, album, directory, album_has_multiple_discs, format=format
            )

        for goodie in album.get("goodies", []):
            if goodie["file_format_id"] != 21:
                self._logger.info("Skipping goodie with unknown file_format_id")
                continue
            goodie_filename = directory / self._sanitize_filename(
                f"{goodie['name']}.pdf"
            )
            self._dlqueue.append(dict(url=goodie["url"], filename=goodie_filename))

    def _save_flac_tags(self, filename: Path, track: dict, album: dict) -> None:
        self._logger.debug(f"Saving tags to {filename}")
        m = mutagen.flac.FLAC(filename)

        def copy_substruct(name: str) -> None:
            val = track.get(name, {}).get("name", None)
            if val is not None:
                m[name] = val

        def copy_val(name: str) -> None:
            val = track.get(name, None)
            if val is not None:
                m[name] = val

        copy_val("title")

        m["album"] = album["title"]
        if "upc" in album:
            m["productnumber"] = album["upc"]
        m["tracknumber"] = str(track["track_position"])
        m["discnumber"] = str(track["track_disc"])
        # Unique artists in set of artists
        m["artist"] = list(dict.fromkeys(a["name"] for a in album["artists"]))

        copy_val("copyright")
        copy_val("isrc")
        copy_substruct("composer")
        copy_substruct("performer")
        copy_substruct("genre")

        m["date"] = datetime.fromtimestamp(track["album"]["released_at"]).strftime(
            "%Y-%m-%d"
        )

        if "_cover" in album:
            cover: Image = album["_cover"]["image"]

            flacpic = mutagen.flac.Picture()
            flacpic.type = mutagen.id3.PictureType.COVER_FRONT
            flacpic.mime = "image/jpeg"
            flacpic.width = cover.width
            flacpic.height = cover.height
            flacpic.depth = 24
            flacpic.data = album["_cover"]["data"]
            m.add_picture(flacpic)

        m.save()

    def _fixup_id3_tags(self, mp3_file: Path, track: dict, album: dict) -> None:
        # ffmpeg converts the FLAC tags to ID3, but they aren't completely correct
        m = mutagen.mp3.MP3(mp3_file)
        # Performer is saved as "Conductor" (TPE3)
        if "performer" in track:
            m.tags.setall("TPE2", [mutagen.id3.TPE2(text=track["performer"]["name"])])
            m.tags.setall("TOPE", [mutagen.id3.TOPE(text=track["performer"]["name"])])
            m.tags.delall("TPE3")
        # ISRC is not converted currently
        if "isrc" in track:
            m.tags.add(mutagen.id3.TSRC(text=track["isrc"]))
        # Remove unconverted tags
        m.tags.delall("TXXX")
        m.save()

    async def _convert_to_mp3(self, flac_file: Path) -> Path:
        mp3_file = flac_file.with_suffix(".mp3")
        self._logger.debug(f"Converting {flac_file} to {mp3_file}")

        # Wrap ffpb notifier with async processing
        with ffpb.ProgressNotifier() as notifier:
            cmd = [
                "ffmpeg",
                "-i",
                str(flac_file),
                # CBR 320kbps
                "-ab",
                "320k",
                # Copy cover art as-is (don't covert to PNG)
                "-c:v",
                "copy",
                # Overwrite output
                "-y",
                str(mp3_file),
            ]
            p = await asyncio.create_subprocess_exec(*cmd, stderr=subprocess.PIPE)

            while True:
                out = await p.stderr.read(1)
                if out == b"":
                    break

                notifier(out)

            await p.wait()

            if p.returncode != 0:
                raise RuntimeError(f"ffmpeg exited with return code {p.returncode}")

        return mp3_file

    def _download_track(
        self,
        track: dict,
        album: dict,
        directory: Path,
        album_has_multiple_discs: bool,
        format: str,
    ) -> None:
        track_id = track["id"]
        self._logger.debug(f"Processing track ID {track_id} / {track['title']}")
        audio = self._audios_by_track_id[track_id]

        if audio["mime_type"] != "audio/flac":
            raise RuntimeError(
                f"Format {audio['mime_type']} not supported on track {track_id} - only FLAC is supported"
            )

        track_no = (
            f"{track['track_disc']}-{track['track_position']:02}"
            if album_has_multiple_discs
            else f"{track['track_position']:02}"
        )
        filename = directory / self._sanitize_filename(
            f"{track_no} - {track['title']}.flac"
        )

        async def postprocess_track(filename: Path) -> None:
            self._save_flac_tags(filename, track, album)
            if format == "mp3":
                mp3_file = await self._convert_to_mp3(filename)
                self._fixup_id3_tags(mp3_file, track, album)
                # Remove FLAC after processing
                filename.unlink()
            elif format == "flac":
                # Nothing to do
                pass
            else:
                raise ValueError(f"Unknown format {format}")

        self._dlqueue.append(
            dict(url=audio["url"], filename=filename, postprocess=postprocess_track)
        )

    def _sanitize_filename(self, filename: str) -> str:
        return pathvalidate.sanitize_filename(filename, replacement_text="_")


def main() -> None:
    parser = OptionParser(usage="usage: %prog [options] qbzdl-url...")
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="show extra messages during processing",
    )
    parser.add_option(
        "-F",
        "--flac",
        action="store_true",
        dest="flac",
        help="keep FLAC files instead of converting to MP3",
    )
    parser.add_option(
        "-r",
        "--register",
        dest="register",
        help="register MIME handler in specified mode (pip or poetry) and exit",
    )

    options, args = parser.parse_args()

    if options.register:
        if options.register == "poetry":
            cmd = "poetry run qbzstoredl"
            path = Path(__file__).parent.parent
        elif options.register == "pip":
            cmd = "qbzstoredl"
            path = ""
        else:
            raise RuntimeError(f"Invalid --register option {options.register}")

        (
            Path.home() / ".local" / "share" / "applications" / "qbzstoredl.desktop"
        ).write_text(
            f"""[Desktop Entry]
Type=Application
Name=qbzstoredl
Exec={cmd} %u
{f"Path={path}" if path else ""}
StartupNotify=false
Terminal=true
MimeType=x-scheme-handler/qbzdl;
"""
        )
        subprocess.run(
            ["xdg-mime", "default", "qbzstoredl.desktop", "x-scheme-handler/qbzdl"],
            check=True,
        )
        return

    logging.basicConfig(level=logging.DEBUG if options.verbose else logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.INFO)

    async def main() -> None:
        q = QobuzDownloader()
        for url in args:
            await q.enqueue_download(url, format="flac" if options.flac else "mp3")
        await q.run()

    asyncio.run(main())


if __name__ == "__main__":
    main()
