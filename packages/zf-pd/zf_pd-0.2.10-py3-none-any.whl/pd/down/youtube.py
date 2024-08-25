from re import sub as re_sub

from loguru import logger
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi


def get_script(url: str) -> (str, str):
    yt = YouTube(url)
    title = re_sub(r'[\/:*?"<>|]', '', yt.title)

    if 'youtube.com' in url:
        url = url.split('=')[-1]

    subtitles = YouTubeTranscriptApi.get_transcript(url)

    script = " ".join([f"{sub['text']}" for sub in subtitles])
    return title, script


if __name__ == '__main__':
    link = f"https://www.youtube.com/watch?v=DxREm3s1scA"
    t, s = get_script(link)
    logger.info(f"{t}: {s}")
