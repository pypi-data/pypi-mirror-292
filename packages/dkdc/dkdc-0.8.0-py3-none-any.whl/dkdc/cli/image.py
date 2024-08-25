# imports
import os
import cairosvg

from PIL import Image
from dkdc.cli.console import print


# functions
def resize_image(input_path: str, output_path: str, height: int, width: int) -> None:
    """
    Resize an image.
    """
    print(f"resizing image: {input_path} -> {output_path} ({height}x{width})")
    if input_path.lower().endswith(".svg"):
        png_path = input_path.replace(".svg", ".png")
        cairosvg.svg2png(url=input_path, write_to=png_path)
        input_path = png_path

    with Image.open(input_path) as img:
        resized_img = img.resize((height, width))
        resized_img.save(output_path)


def convert_image(
    input_path: str,
    output_path: str = None,
    output_format: str = "png",
):
    """
    convert an image to a different format
    """
    if output_path:
        output_format = os.path.splitext(output_path)[1][1:]
    else:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.{output_format}"

    print(f"converting image: {input_path} -> {output_path} ({output_format})")
    if input_path.lower().endswith(".svg"):
        if output_format.lower() == "png":
            cairosvg.svg2png(url=input_path, write_to=output_path)
        elif output_format.lower() == "pdf":
            cairosvg.svg2pdf(url=input_path, write_to=output_path)
        elif output_format.lower() == "ps":
            cairosvg.svg2ps(url=input_path, write_to=output_path)
        else:
            raise ValueError(f"Unsupported output format for SVG: {output_format}")
    else:
        with Image.open(input_path) as img:
            img.save(output_path, format=output_format.upper())
