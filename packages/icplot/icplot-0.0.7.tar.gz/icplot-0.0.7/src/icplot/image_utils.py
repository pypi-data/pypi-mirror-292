import logging
from pathlib import Path

from wand.image import Image
from wand.color import Color

import cairosvg

logger = logging.getLogger(__name__)


def _get_out_filename(source: Path, target: Path | None, extension: str) -> Path:
    if target:
        return target
    else:
        return source.parent / f"{source.stem}.{extension}"


def pdf_to_png(source: Path, target: Path | None = None):

    outfile = _get_out_filename(source, target, "png")
    with Image(filename=source, resolution=300) as img:
        img.format = "png"
        img.background_color = Color("white")
        img.alpha_channel = "remove"
        img.save(filename=outfile)


def svg_to_png(source: Path, target: Path | None = None):
    outfile = _get_out_filename(source, target, "png")
    cairosvg.svg2png(url=str(source), write_to=str(outfile))


def svg_to_pdf(source: Path, target: Path | None = None):
    outfile = _get_out_filename(source, target, "pdf")
    cairosvg.svg2pdf(url=str(source), write_to=str(outfile))
