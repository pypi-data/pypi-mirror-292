from glob import glob
from os import makedirs
from os import path as os_path
from typing import List, Tuple

from click import Path, argument, group, option
from loguru import logger
from PIL import Image, ImageDraw, ImageFilter

from pd.__model__.utils import parse_str_list_int


@group(name="edit", help="Edit a file")
def edit():
    pass

@edit.command(help="Size an image")
@argument("filepaths", nargs=-1, type=Path(exists=True), required=True)
def size(filepaths: Tuple[str, ...]):
    for path in filepaths:
        img = Image.open(path).convert("RGBA")
        width, height = img.size
        filename = os_path.basename(path)
        logger.info(f"Image {filename}: {width}x{height} pixels")


@edit.command(help="Round an image")
@option("-p", "--path", type=str, required=True, prompt=True, help="Input image file path")
@option("-r", "--radius", type=str, default="20%", show_default=True, help="Radius (pixels or percentage)")
def round(path: str, radius: str):
    img = Image.open(path).convert("RGBA")
    width, height = img.size

    radius_px = radius_to_pixels(radius, width, height)
    rounded_img = round_corners(img, radius_px)

    file_name, file_ext = os_path.splitext(path)
    new_file_name = f"{file_name}_rounded{width}x{height}.png"

    rounded_img.save(new_file_name, "PNG")
    logger.info(f"Rounded image saved as {new_file_name}")


@edit.command(help="Resize image(s)")
@option("-s", "--size", type=int, help="Size of longer side (pixels)")
@option("-d", "--dimensions", callback=parse_str_list_int, type=str, help="Dimensions in pixels e.g. 512x512")
@option("-o", "--output", type=str, default="", help="Output folder path (optional)")
@option("-n", "--no-suffix", is_flag=True, help="Don't add size suffix to output filename")
@argument("filepaths", nargs=-1, type=Path(exists=True), required=True)
def resize(size: int, dimensions: list[int], output: str, no_suffix: bool, filepaths: Tuple[str, ...]):
    if len(dimensions) != 2 and not size:
        logger.error("Please provide either a size or two dimensions")
        return

    if output:
        makedirs(output, exist_ok=True)

    for input_file in filepaths:
        img = Image.open(input_file).convert("RGBA")
        width, height = img.size
        logger.info(f"Original size: {width}x{height}")

        if dimensions:
            new_dims = (dimensions[0], dimensions[1])
        else:
            longer_side = max(width, height)
            scale = size / longer_side
            new_dims = (int(width * scale), int(height * scale))

        img = high_quality_resize(img, new_dims)

        file_name, file_ext = os_path.splitext(os_path.basename(input_file))
        if no_suffix:
            new_file_name = f"{file_name}{file_ext}"
        else:
            new_file_name = f"{file_name}_{new_dims[0]}x{new_dims[1]}{file_ext}"

        if output:
            new_file_path = os_path.join(output, new_file_name)
        else:
            new_file_path = os_path.join(os_path.dirname(input_file), new_file_name)

        img.save(new_file_path, format=file_ext[1:].upper())
        logger.info(f"Resized image saved as {new_file_path}")

    logger.info(f"Resized {len(filepaths)} image(s)")


@edit.command(help="Scale an image")
@option("-p", "--path", type=str, required=True, prompt=True, help="Input image file path")
@option("-s", "--scale", type=float, required=True, prompt=True, help="Scale factor")
def scale(path: str, scale: float):
    img = Image.open(path).convert("RGBA")

    size = (int(img.size[0] * scale), int(img.size[1] * scale))
    img = high_quality_resize(img, size)

    file_name, file_ext = os_path.splitext(path)
    new_file_name = f"{file_name}_{size[0]}x{size[1]}.png"

    img.save(new_file_name, "PNG")
    logger.info(f"Scaled image saved as {new_file_name}")


@edit.command(help="Generate logos from an image")
@option("-p", "--path", type=str, required=True, prompt=True, help="Input image file path")
@option(
    "-t",
    "--template",
    type=str,
    default="Generic=(16, 32, 48, 128, 256, 512, 1024)",
    show_default=True,
    help="Template for logo sizes",
)
@option("-s", "--sizes", callback=parse_str_list_int, type=str, default="", show_default=True, help="Sizes for icon")
@option("-r", "--radius", type=str, default="", show_default=True, help="Radius (pixels or percentage)")
def logos(path: str, template: str, sizes: List[int], radius: str):
    logger.debug("logo")

    original_image = Image.open(path).convert("RGBA")
    width, height = original_image.size

    # Ensure the image is square
    if width != height:
        logger.warning("Image is not square. Cropping to make it square.")
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        original_image = original_image.crop((left, top, right, bottom))

    # Get sizes from template
    template = "Generic" if "Generic" in template else template
    logo_sizes = sizes if sizes else get_sizes_from_template(template)

    # Check if upscaling is needed
    max_size = max(logo_sizes)
    if original_image.size[0] < max_size:
        logger.info(f"Upscaling image to {max_size}x{max_size}")
        original_image = high_quality_resize(original_image, (max_size, max_size))

    if radius:
        radius_px = radius_to_pixels(radius, original_image.size[0], original_image.size[1])
        logger.info(f"Rounding corners with radius {radius_px}")
        original_image = round_corners(original_image, radius_px)

    # Generate all sizes
    for size in logo_sizes:
        resized_image = high_quality_resize(original_image, (size, size))

        # Generate output filename
        file_name, file_ext = os_path.splitext(path)
        output_path = f"{file_name}{size}{file_ext}"

        # Save the resized image
        resized_image.save(output_path)
        logger.debug(f"Generated logo: {output_path}")

    logo_sizes = [f"{size}x{size}" for size in logo_sizes]
    logger.info(f"{len(logo_sizes)} logos ({', '.join(logo_sizes)}) and saved in the same directory")


@edit.command(help="Generate favicon from an image")
@option("-p", "--path", type=str, required=True, prompt=True, help="Input image file path")
@option("-s", "--sizes", type=list, default=[16, 32, 48], show_default=True, help="Sizes for icon")
def favicon(path: str, sizes: List[int]):
    original_image = Image.open(path).convert("RGBA")

    icon_sizes = []
    for size in sizes:
        resized_image = high_quality_resize(original_image, (size, size))
        icon_sizes.append(resized_image)

    output_path = f"{os_path.splitext(path)[0]}.ico"
    icon_sizes[0].save(output_path, format="ICO", sizes=[(size, size) for size in sizes], append_images=icon_sizes[1:])

    logger.info(f"Icon created successfully: {output_path}")
    logger.info(f"Icon sizes: {sizes}")


def radius_to_pixels(radius: str, width: int, height: int) -> int:
    if not radius:
        return 0
    if radius.endswith("%"):
        percentage = float(radius[:-1]) / 100
        return int(min(width, height) * percentage / 2)
    else:
        return int(radius)


def round_corners(img: Image, radius: int) -> Image:
    circle = Image.new("L", (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new("L", img.size, 255)
    w, h = img.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    img.putalpha(alpha)
    return img


def high_quality_resize(image: Image, size: Tuple[int, int]) -> Image:
    factor = 8
    img = image.copy()
    img.thumbnail((size[0] * factor, size[1] * factor), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    img = img.resize(size, Image.LANCZOS)
    return img


def get_sizes_from_template(template: str) -> List[int]:
    if template == "iOS":
        return [40, 60, 80, 120, 180]
    elif template == "Android":
        return [36, 48, 64, 72, 96, 144, 192]
    elif template == "macOS":
        return [16, 32, 128, 256, 512]
    elif template == "Chrome":
        return [16, 19, 32, 38, 48, 128]
    elif template == "Generic":
        return [16, 32, 48, 128, 256, 512, 1024]
    else:
        raise ValueError(f"Unsupported template: {template}")
