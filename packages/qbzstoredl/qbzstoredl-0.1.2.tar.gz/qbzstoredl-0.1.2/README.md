Downloader for music from the Qobuz download store
==================================================

Qobuz recently discontinued support for tarball downloads.
Instead, you now have to use their Qobuz Downloader app that is not available on Linux.
Since the Downloader app never worked for me anyway and I like to use Linux, I have made this script to act as a replacement for the Downloader on Linux.

Installation
------------

Prerequisites:
* Python 3.11 (other versions might also work, not tested)
* [poetry](https://python-poetry.org/docs/)
* [ffmpeg](https://ffmpeg.org/)

### From pip

```
pip install qbzstoredl
qbzstoredl --register pip
```

### From git

```
git clone https://gitlab.com/pkerling/qbzstoredl.git
cd qbzstoredl
poetry install
poetry run qbzstoredl --register poetry
```

### MIME handler

The last step registers an URL handler for the `qbzdl` scheme that is used by the official downloader and allows any browser to just launch the script from the normal Qobuz download page.
Be aware that it will not work any more and you need to rerun `qbzstoredl --register` if you move the directory containing this repository.

Usage
-----

1. Log in to Qobuz in your browser.
1. Go to "My purchases" or open a download link from a successful purchase email.
1. Click "Download with Qobuz Downloader".
1. Click "Open" in the popup.
1. Depending on your browser, allow the URL to be opened with qbzstoredl.
1. Watch as the music is being downloaded to your "Downloads" folder.

### Manual usage

On the Qobuz download page, note the URL starting with `qbzdl://` resulting from the click on "Open" in the download popup.
You can use it on the terminal like this: `poetry run qbzstoredl qbzdl://...`

Notes
-----

As far as I could tell, the Downloader always downloads the FLAC version of the tracks.
If MP3 is desired, it is converted on the user's PC, so this is what this script also does.

I have tested this only with a few albums in my own collection, which exclusively contains CD quality albums, so YMMV.
Feel free to report problems, but I will likely not be able to help without the `qbzdl://` URL for the download, which you can send me privately.
