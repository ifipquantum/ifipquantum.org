#!/usr/bin/env python3
"""Generate the favicon set from images/ifipqc-logo.svg using Inkscape.

The generated files are committed, so this only needs re-running when the logo
changes:

    ./util/make_favicons.py
"""

import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "images" / "ifipqc-logo.svg"
BACKGROUND = "#130D2B"  # --color-charcoal, the site background
ICO_SIZES = (16, 32, 48)


def padded_svg(padding: int, out: Path) -> Path:
    """Re-frame the logo by growing its viewBox: `padding` units on each side of
    the 100x100 artwork. Inkscape's --export-area works in px rather than user
    units, so padding this way keeps things independent of the document size."""
    box = f"-{padding} -{padding} {100 + 2 * padding} {100 + 2 * padding}"
    svg = SOURCE.read_text().replace('viewBox="0 0 100 100"', f'viewBox="{box}"', 1)
    out.write_text(svg)
    return out


def render(src: Path, out: Path, size: int, opaque: bool = False) -> None:
    args = [
        "inkscape",
        str(src),
        "--export-type=png",
        f"--export-filename={out}",
        f"--export-width={size}",
        f"--export-height={size}",
    ]
    if opaque:
        args += [f"--export-background={BACKGROUND}", "--export-background-opacity=1"]
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


def write_ico(out: Path, pngs: list[tuple[int, bytes]]) -> None:
    """Pack the small PNGs into an ICO container (PNG-compressed entries)."""
    offset = 6 + 16 * len(pngs)
    entries = b""
    for size, png in pngs:
        entries += struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(png), offset)
        offset += len(png)
    header = struct.pack("<HHH", 0, 1, len(pngs))
    out.write_bytes(header + entries + b"".join(png for _, png in pngs))


def main() -> None:
    if shutil.which("inkscape") is None:
        sys.exit("inkscape must be on the PATH")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        plain = padded_svg(0, tmp / "plain.svg")
        apple = padded_svg(13, tmp / "apple.svg")  # iOS rounds the corners itself
        maskable = padded_svg(25, tmp / "maskable.svg")  # Android crops to a circle

        # SVG favicon: scalable, preferred over the PNGs by Chrome and Firefox.
        shutil.copyfile(plain, ROOT / "favicon.svg")

        render(plain, ROOT / "images" / "icon-192.png", 192)
        render(plain, ROOT / "images" / "icon-512.png", 512)
        render(plain, ROOT / "images" / "icon-opaque-512.png", 512, opaque=True)
        render(maskable, ROOT / "images" / "icon-maskable-512.png", 512, opaque=True)
        # iOS ignores transparency, so give the Apple icon the site background.
        render(apple, ROOT / "apple-touch-icon.png", 180, opaque=True)

        pngs = []
        for size in ICO_SIZES:
            png = tmp / f"{size}.png"
            render(plain, png, size)
            pngs.append((size, png.read_bytes()))
        write_ico(ROOT / "favicon.ico", pngs)

    print(
        "wrote favicon.ico favicon.svg apple-touch-icon.png "
        "images/icon-{192,512,opaque-512,maskable-512}.png"
    )


if __name__ == "__main__":
    main()
