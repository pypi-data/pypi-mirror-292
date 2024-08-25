from os import getcwd
from os import path as os_path
from typing import Dict
from uuid import uuid4

from click import Path, argument, group, option
from loguru import logger
from moviepy.editor import ImageClip
from PIL import Image
from pydantic import BaseModel

from .audio import m4a, mp3
from .epub import epub
from .text import txt
from .video import mov, mp4, webm


class FileSource(BaseModel):
    name: str
    ext: str
    path: str

    _filename: str | None = None

    @property
    def filename(self):
        if not self._filename:
            self._filename = f"{self.name}.{self.ext}"
        return self._filename

    def __repr__(self):
        return f"FileSource(name={self.name}, ext={self.ext}, path={self.path})"

    class Config:
        frozen = True


@group(name="conv", help="Convert a file")
def conv():
    pass


@conv.command(help="Convert an image or multiple images into another format")
@option("-f", "--format", type=str, required=True, prompt=True, help="Format to convert to (e.g. jpg, mp4)")
@option("-d", "--duration", type=int, default=0, help="Duration of output file in seconds (e.g. 30)")
@argument("filepaths", nargs=-1, type=Path(exists=True), required=True)
def image(format: str, duration: int, filepaths: tuple[str, ...]):
    for input_path in filepaths:
        src_file, dst_file = generate_file_sources(input_path, format)

        logger.info(f"Converting {src_file.filename} to {dst_file.filename}")

        match dst_file.ext:
            case "jpg" | "jpeg" | "png" | "webp":
                with Image.open(src_file.path) as image:
                    image.save(dst_file.path, format.upper())
            case "mp4":
                clip = ImageClip(src_file.path, duration=duration)
                clip.write_videofile(dst_file.path, fps=24, codec="libx264")
            case _:
                logger.error(f"Unsupported format {dst_file.ext}")

    logger.info(f"Converted {len(filepaths)} image(s)")


@conv.command(help="Convert an audio to another format")
@option("-f", "--format", type=str, required=True, prompt=True, help="Format to convert to (e.g. wav)")
@argument("filepaths", nargs=-1, type=Path(exists=True), required=True)
def audio(format: str, filepaths: tuple[str, ...]):
    for filepath in filepaths:
        src_file, dst_file = generate_file_sources(filepath, format)

        logger.info(f"Converting {src_file.path} to {dst_file.path}")

        match src_file.ext:
            case "m4a":
                m4a(src_file.path, dst_file.path)
            case "mp3":
                mp3(src_file.path, dst_file.path)
            case _:
                logger.error(f"Unsupported file {src_file.ext}")


@conv.command(help="Convert a video to another format")
@option("-f", "--format", type=str, required=True, prompt=True, help="Format to convert to (e.g. mp3)")
@argument("filepaths", nargs=-1, type=Path(exists=True), required=True)
def video(format: str, filepaths: tuple[str, ...]):
    for filepath in filepaths:
        src_file, dst_file = generate_file_sources(filepath, format)

        logger.info(f"Converting {src_file.path} to {dst_file.path}")

        match src_file.ext:
            case "mp4":
                mp4(src_file.path, dst_file.path)
            case "webm":
                webm(src_file.path, dst_file.path)
            case "mov":
                mov(src_file.path, dst_file.path)
            case _:
                logger.error(f"Unsupported file {src_file.ext}")


@conv.command(help="Convert text into another format")
@option("-v", "--value", type=str, required=True, prompt=True, help="Text to convert")
@option("-f", "--format", type=str, required=True, prompt=True, help="Format to convert to (e.g. mp3)")
@option(
    "-o",
    "--options",
    type=str,
    required=False,
    default="voice=echo",
    help="Options to use for conversion (e.g. voice=alloy)",
)
def text(value: str, format: str, options: str):
    logger.debug("conv text")

    dst_format = format
    dst_path = f"{str(uuid4())}.{dst_format}"

    logger.debug(f"Converting {value} to {format} at ./{dst_path}")

    opts: Dict[str, str] = {k: v.lower() for k, v in [o.split("=") for o in options.split(",")]}

    txt(value, dst_path, opts)
    return


@conv.command(help="Convert a book into another format")
@option("-p", "--path", type=str, required=True, prompt=True, help="Path to the book file (e.g. /path/to/file)")
@option("-f", "--format", type=str, required=True, prompt=True, help="Format to convert to (e.g. pdf)")
def book(path: str, format: str) -> None:
    logger.debug("conv book")

    if not os_path.isabs(path):
        path = os_path.join(getcwd(), path)

    if not os_path.exists(path):
        print(f"Book {path} does not exist")
        return

    splits = path.split(".")

    src_format = splits[-1]
    src_filename = ".".join(splits[:-1])
    src_path = path

    dst_format = format
    dst_path = f"{src_filename}.{dst_format}"

    logger.debug(f"Converting {src_path} to {dst_path}")

    if src_format == "epub":
        epub(src_path, dst_path)
    else:
        logger.error(f"Unsupported file {src_format}")
    return


def generate_file_sources(src_filepath: str, dst_format: str) -> tuple[FileSource]:
    if not os_path.isabs(src_filepath):
        src_filepath = os_path.join(getcwd(), src_filepath)

    if not os_path.exists(src_filepath):
        logger.error(f"File {src_filepath} does not exist")
        raise FileNotFoundError

    src_filename, src_format = os_path.splitext(os_path.basename(src_filepath))
    src_format = src_format[1:]
    src_dirpath = os_path.dirname(src_filepath)
    src_filepath = src_filepath

    return (
        FileSource(name=src_filename, ext=src_format, path=src_filepath),
        FileSource(name=src_filename, ext=dst_format, path=os_path.join(src_dirpath, f"{src_filename}.{dst_format}")),
    )
