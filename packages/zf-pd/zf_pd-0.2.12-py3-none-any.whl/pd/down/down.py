from click import group
from click import option
from loguru import logger
from pytubefix import YouTube

from .libgen import download_book
from .youtube import get_script


@group(name='down', help="Download from the internet")
def down():
    pass


@down.command(help="Download a YouTube video")
@option('-l', '--link', type=str, required=True, prompt=True,
        help="Link to the YouTube video (e.g. https://www.youtube.com/watch?v=...)")
@option('-f', '--format', type=str, required=True, prompt=True,
        help="Format to download as (e.g. mp4, mp3, txt)")
def youtube(link: str, format: str):
    logger.debug("down video")

    if format == 'mp4':
        yt = YouTube(link)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download()
    elif format == 'mp3':
        yt = YouTube(link)
        stream = yt.streams.get_audio_only()
        stream.download(mp3=True)
    elif format == 'webm':
        yt = YouTube(link)
        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        stream.download()
    elif format == 'txt':
        title, script = get_script(link)
        with open(f"{title}.txt", 'w') as f:
            f.write(script)
    else:
        logger.error(f"Unsupported format {format}")


@down.command(help="Download a book from Libgen")
@option('-n', '--name', type=str, required=True, prompt=True,
        help="Author name")
@option('-t', '--title', type=str, required=True, prompt=True,
        help="Book title")
def libgen(name: str, title: str):
    logger.debug("down book")
    download_book(name, title)
