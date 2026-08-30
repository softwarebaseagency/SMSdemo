from __future__ import annotations

import copy
import hashlib
import json
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont

try:
    import uharfbuzz as hb
except Exception:  # pragma: no cover
    hb = None

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # pragma: no cover
    Image = ImageDraw = ImageFont = None


ROOT = Path(__file__).resolve().parent
UPSTREAM_ZIP = ROOT / "tmp" / "Inter-4.1.zip"
DIST = ROOT / "dist-base-meridion-english"
FONTS = DIST / "fonts"
SPECIMEN = DIST / "specimen"
DOCS = DIST / "documentation"
SOURCE = DIST / "source"

FAMILY = "Base Meridion English"
FILE_PREFIX = "BaseMeridionEnglish"
VERSION = "1.002"
VENDOR_ID = "BASE"

ARABIC_DOT_RANGES = [
    (0x0600, 0x06FF),
    (0x0750, 0x077F),
    (0x0870, 0x089F),
    (0x08A0, 0x08FF),
    (0xFB50, 0xFDFF),
    (0xFE70, 0xFEFF),
]


@dataclass(frozen=True)
class Style:
    suffix: str
    typographic_style: str
    weight: int
    italic: bool
    upstream_file: str

    @property
    def file_stem(self) -> str:
        return f"{FILE_PREFIX}-{self.suffix}"

    @property
    def postscript(self) -> str:
        return self.file_stem

    @property
    def full_name(self) -> str:
        return f"{FAMILY} {self.typographic_style}"

    @property
    def legacy_family(self) -> str:
        if self.typographic_style in {"Regular", "Italic", "Bold", "Bold Italic"}:
            return FAMILY
        return f"{FAMILY} {self.typographic_style.replace(' Italic', '')}"

    @property
    def legacy_subfamily(self) -> str:
        if self.typographic_style in {"Regular", "Italic", "Bold", "Bold Italic"}:
            return self.typographic_style
        return "Italic" if self.italic else "Regular"


STYLES = [
    Style("Thin", "Thin", 100, False, "Inter-Thin.ttf"),
    Style("ThinItalic", "Thin Italic", 100, True, "Inter-ThinItalic.ttf"),
    Style("ExtraLight", "ExtraLight", 200, False, "Inter-ExtraLight.ttf"),
    Style("ExtraLightItalic", "ExtraLight Italic", 200, True, "Inter-ExtraLightItalic.ttf"),
    Style("Light", "Light", 300, False, "Inter-Light.ttf"),
    Style("LightItalic", "Light Italic", 300, True, "Inter-LightItalic.ttf"),
    Style("Regular", "Regular", 400, False, "Inter-Regular.ttf"),
    Style("Italic", "Italic", 400, True, "Inter-Italic.ttf"),
    Style("Medium", "Medium", 500, False, "Inter-Medium.ttf"),
    Style("MediumItalic", "Medium Italic", 500, True, "Inter-MediumItalic.ttf"),
    Style("SemiBold", "SemiBold", 600, False, "Inter-SemiBold.ttf"),
    Style("SemiBoldItalic", "SemiBold Italic", 600, True, "Inter-SemiBoldItalic.ttf"),
    Style("Bold", "Bold", 700, False, "Inter-Bold.ttf"),
    Style("BoldItalic", "Bold Italic", 700, True, "Inter-BoldItalic.ttf"),
    Style("Black", "Black", 900, False, "Inter-ExtraBold.ttf"),
    Style("BlackItalic", "Black Italic", 900, True, "Inter-ExtraBoldItalic.ttf"),
    Style("Super", "Super", 1000, False, "Inter-Black.ttf"),
    Style("SuperItalic", "Super Italic", 1000, True, "Inter-BlackItalic.ttf"),
]


def arabic_dot_name(cp: int) -> str:
    return f"arabicdot{cp:04X}"


def set_name(font: TTFont, name_id: int, value: str) -> None:
    table = font["name"]
    table.names = [record for record in table.names if record.nameID != name_id]
    table.setName(value, name_id, 3, 1, 0x0409)
    table.setName(value, name_id, 1, 0, 0)


def extract_upstream_font(style: Style, work: Path) -> Path:
    if not UPSTREAM_ZIP.exists():
        raise FileNotFoundError(f"Missing upstream Inter zip: {UPSTREAM_ZIP}")
    member = f"extras/ttf/{style.upstream_file}"
    with zipfile.ZipFile(UPSTREAM_ZIP) as zf:
        zf.extract(member, work)
    return work / member


def add_arabic_dot_glyphs(font: TTFont) -> None:
    glyph_order = list(font.getGlyphOrder())
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    period_glyph = copy.deepcopy(glyf["period"])
    period_metrics = hmtx.metrics["period"]

    for start, end in ARABIC_DOT_RANGES:
        for cp in range(start, end + 1):
            name = arabic_dot_name(cp)
            if name not in glyf.glyphs:
                glyph_order.append(name)
                glyf.glyphs[name] = copy.deepcopy(period_glyph)
                hmtx.metrics[name] = period_metrics

    font.setGlyphOrder(glyph_order)
    font["maxp"].numGlyphs = len(glyph_order)

    for table in font["cmap"].tables:
        if table.isUnicode():
            for start, end in ARABIC_DOT_RANGES:
                for cp in range(start, end + 1):
                    table.cmap[cp] = arabic_dot_name(cp)

    addOpenTypeFeaturesFromString(
        font,
        "languagesystem DFLT dflt;\n"
        "languagesystem latn dflt;\n"
        "languagesystem arab dflt;\n"
        "feature init {\n"
        "  sub arabicdot0627 by arabicdot0627;\n"
        "} init;\n",
    )


def update_metadata(font: TTFont, style: Style) -> None:
    set_name(font, 0, "Copyright (c) 2026 Base Agency modifications. Original source licensed under the SIL Open Font License 1.1.")
    set_name(font, 1, style.legacy_family)
    set_name(font, 2, style.legacy_subfamily)
    set_name(font, 3, f"BaseAgency:{style.postscript}:{VERSION}:2026")
    set_name(font, 4, style.full_name)
    set_name(font, 5, f"Version {VERSION}")
    set_name(font, 6, style.postscript)
    set_name(font, 7, f"{FAMILY} is a trademark of Base Agency.")
    set_name(font, 8, "Base Agency")
    set_name(font, 9, "Base Agency Type Studio")
    set_name(font, 10, "Base Meridion English is an OFL derivative neutral sans with Arabic-script characters mapped to period dots.")
    set_name(font, 13, "This derivative font software is licensed under the SIL Open Font License 1.1. See LICENSE-OFL.txt.")
    set_name(font, 14, "https://openfontlicense.org")
    set_name(font, 16, FAMILY)
    set_name(font, 17, style.typographic_style)
    set_name(font, 18, style.full_name)
    set_name(font, 21, FAMILY)
    set_name(font, 22, style.typographic_style)

    if "OS/2" in font:
        font["OS/2"].achVendID = VENDOR_ID
        font["OS/2"].usWeightClass = style.weight
        font["OS/2"].fsSelection |= 0x80
        if style.italic:
            font["OS/2"].fsSelection |= 0x01
        if style.weight == 400 and not style.italic:
            font["OS/2"].fsSelection |= 0x40
    if "head" in font:
        font["head"].macStyle = (1 if style.weight >= 700 else 0) | (2 if style.italic else 0)


def build_style(style: Style, work: Path) -> Path:
    src = extract_upstream_font(style, work)
    font = TTFont(src)
    add_arabic_dot_glyphs(font)
    update_metadata(font, style)
    out = FONTS / f"{style.file_stem}.ttf"
    font.save(out)

    web = TTFont(out)
    web.flavor = "woff2"
    web.save(FONTS / f"{style.file_stem}.woff2")
    return out


def write_css() -> None:
    faces = []
    for style in STYLES:
        faces.append(
            "\n".join(
                [
                    "@font-face {",
                    f'  font-family: "{FAMILY}";',
                    f'  src: url("./{style.file_stem}.woff2") format("woff2"), url("./{style.file_stem}.ttf") format("truetype");',
                    f"  font-weight: {style.weight};",
                    f"  font-style: {'italic' if style.italic else 'normal'};",
                    "  font-display: swap;",
                    "}",
                ]
            )
        )
    (FONTS / "base-meridion-english.css").write_text("\n\n".join(faces) + "\n", encoding="utf-8")


def shape_names(font_path: Path, cps: list[int]) -> list[str]:
    if hb is None:
        return []
    font_data = font_path.read_bytes()
    face = hb.Face(font_data)
    hb_font = hb.Font(face)
    hb.ot_font_set_funcs(hb_font)
    buf = hb.Buffer()
    buf.add_str("".join(chr(cp) for cp in cps))
    buf.guess_segment_properties()
    hb.shape(hb_font, buf)
    order = TTFont(font_path).getGlyphOrder()
    return [order[info.codepoint] for info in buf.glyph_infos]


def write_docs(font_paths: list[Path]) -> None:
    with zipfile.ZipFile(UPSTREAM_ZIP) as zf:
        (DOCS / "LICENSE-OFL.txt").write_text(zf.read("LICENSE.txt").decode("utf-8"), encoding="utf-8")

    readme = f"""# {FAMILY} {VERSION}

{FAMILY} is a Base-named OFL derivative built from Inter 4.1, chosen as a lawful high-quality neutral sans source. It is not copied from, renamed from, or traced from Graphik.

Arabic-script Unicode ranges are intentionally mapped to period-dot glyphs, so Arabic/Kurdish-Arabic text displays as dots.

## Included styles

{chr(10).join(f"- `fonts/{style.file_stem}.ttf` and `.woff2`" for style in STYLES)}

## CSS

```css
@import url("./fonts/base-meridion-english.css");

body {{
  font-family: "{FAMILY}", sans-serif;
}}
```

This derivative remains under the SIL Open Font License 1.1. See `documentation/LICENSE-OFL.txt`.
"""
    (DIST / "README.md").write_text(readme, encoding="utf-8")

    source_record = f"""# Design and Source Record

- Family name: {FAMILY}.
- Version: {VERSION}.
- Design direction: neutral geometric/grotesque English sans, selected to sit in the same broad modern brand-sans category without copying Graphik.
- Source: Inter 4.1 release zip from rsms/inter, licensed under SIL Open Font License 1.1.
- Reserved source name handling: the derivative family uses the name `{FAMILY}` and does not use the reserved Inter family name.
- Arabic behavior: Arabic-script ranges U+0600-U+06FF, U+0750-U+077F, U+0870-U+089F, U+08A0-U+08FF, U+FB50-U+FDFF, and U+FE70-U+FEFF map to dot glyphs.
- Requested Graphik files were not copied, traced, renamed, or relicensed.
"""
    (DOCS / "DESIGN-SOURCE-RECORD.md").write_text(source_record, encoding="utf-8")

    report = []
    required = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?.,:;-_()[]{}@#$%&"
    arabic_samples = {
        "salam": [0x0633, 0x0644, 0x0627, 0x0645],
        "kurdish": [0x0643, 0x0648, 0x0631, 0x062F, 0x064A],
        "arabic": [0x0639, 0x0631, 0x0628, 0x064A],
    }
    for path in font_paths:
        font = TTFont(path)
        cmap = {}
        for table in font["cmap"].tables:
            if table.isUnicode():
                cmap.update(table.cmap)
        report.append(
            {
                "file": path.name,
                "family_name": font["name"].getDebugName(1),
                "typographic_family": font["name"].getDebugName(16),
                "style": font["name"].getDebugName(17),
                "postscript_name": font["name"].getDebugName(6),
                "weight": font["OS/2"].usWeightClass,
                "glyphs": font["maxp"].numGlyphs,
                "missing_required_characters": [ch for ch in required if ord(ch) not in cmap],
                "arabic_dot_mapping_ok": all(cmap.get(cp, "").startswith("arabicdot") for cp in arabic_samples["salam"]),
                "arabic_shape_glyphs": {key: shape_names(path, cps) for key, cps in arabic_samples.items()} if path.name.endswith("Regular.ttf") else {},
            }
        )
    (DOCS / "validation-report.json").write_text(
        json.dumps({"family": FAMILY, "version": VERSION, "styles": report}, indent=2),
        encoding="utf-8",
    )


def write_specimen() -> None:
    html_faces = "\n".join(
        f"""@font-face{{font-family:BaseMeridionEnglish;src:url('../fonts/{style.file_stem}.woff2') format('woff2');font-weight:{style.weight};font-style:{'italic' if style.italic else 'normal'};font-display:swap}}"""
        for style in STYLES
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{FAMILY} Specimen</title>
<style>
{html_faces}
*{{box-sizing:border-box}}
body{{margin:0;background:#f6f3ec;color:#111827;font-family:BaseMeridionEnglish,sans-serif}}
header{{padding:7vw 6vw;background:#111827;color:white}}
h1{{font-size:clamp(54px,11vw,160px);line-height:.94;margin:0;font-weight:900}}
header p{{font-size:clamp(26px,4.2vw,60px);margin:.35em 0 0;font-weight:400;color:#d8e2f0}}
main{{padding:5vw 6vw;max-width:1280px;margin:auto}}
section{{border-top:2px solid #111827;padding:32px 0}}
h2{{font-size:22px;text-transform:uppercase;letter-spacing:.06em;margin:0 0 20px;color:#475569}}
p{{font-size:clamp(30px,4.8vw,72px);line-height:1.2;margin:0}}
.alphabet{{font-size:clamp(24px,3.4vw,48px);line-height:1.55;word-break:break-word}}
.medium{{font-weight:500}}.semibold{{font-weight:600}}.bold{{font-weight:700}}.black{{font-weight:900}}.italic{{font-style:italic}}
</style>
</head>
<body>
<header><h1>{FAMILY}</h1><p>Professional neutral sans with Arabic as dots.</p></header>
<main>
<section><h2>Regular</h2><p>Modern systems need clear letters, calm rhythm, and strong names.</p></section>
<section><h2>Medium</h2><p class="medium">Base Meridion English 0123456789</p></section>
<section><h2>Bold Italic</h2><p class="bold italic">Fast structure, clean motion, confident voice.</p></section>
<section><h2>Alphabet</h2><p class="alphabet">ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>abcdefghijklmnopqrstuvwxyz<br>0123456789 !?&amp;@#$% - _ / ( ) [ ] {{ }}</p></section>
<section><h2>Arabic Dot Mapping</h2><p class="alphabet">&#x0633;&#x0644;&#x0627;&#x0645; &#x0643;&#x0648;&#x0631;&#x062F;&#x064A; &#x0639;&#x0631;&#x0628;&#x064A;</p></section>
</main>
</body>
</html>
"""
    (SPECIMEN / "BaseMeridionEnglish-Specimen.html").write_text(html, encoding="utf-8")

    if Image is None:
        return
    img = Image.new("RGB", (1800, 1320), "#f6f3ec")
    draw = ImageDraw.Draw(img)
    regular = ImageFont.truetype(str(FONTS / f"{FILE_PREFIX}-Regular.ttf"), 84)
    bold = ImageFont.truetype(str(FONTS / f"{FILE_PREFIX}-Bold.ttf"), 142)
    medium = ImageFont.truetype(str(FONTS / f"{FILE_PREFIX}-Medium.ttf"), 58)
    semibold = ImageFont.truetype(str(FONTS / f"{FILE_PREFIX}-SemiBold.ttf"), 66)
    draw.rectangle((0, 0, 1800, 390), fill="#111827")
    draw.text((90, 80), FAMILY, font=bold, fill="#ffffff")
    draw.text((95, 278), "Professional neutral sans - Thin to Super", font=medium, fill="#d8e2f0")
    draw.text((95, 470), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", font=semibold, fill="#111827")
    draw.text((95, 590), "abcdefghijklmnopqrstuvwxyz", font=semibold, fill="#1f2937")
    draw.text((95, 720), "0123456789  !? & @ # $ %", font=regular, fill="#334155")
    draw.text((95, 880), "Modern systems need clear letters.", font=regular, fill="#111827")
    arabic_sample = "".join(chr(cp) for cp in [0x0633, 0x0644, 0x0627, 0x0645, 0x20, 0x0643, 0x0648, 0x0631, 0x062F, 0x064A, 0x20, 0x0639, 0x0631, 0x0628, 0x064A])
    draw.text((95, 1045), "Arabic maps to dots: " + arabic_sample, font=medium, fill="#334155")
    img.save(SPECIMEN / "BaseMeridionEnglish-Specimen.png")


def write_hashes() -> None:
    sums = []
    for path in sorted(DIST.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            sums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(DIST).as_posix()}")
    (DOCS / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")


def package_zip() -> Path:
    zip_path = ROOT / f"Base-Meridion-English-{VERSION}-Base-Agency.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(DIST.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(DIST.parent))
    (ROOT / f"{zip_path.name}.sha256").write_text(
        f"{hashlib.sha256(zip_path.read_bytes()).hexdigest()}  {zip_path.name}\n",
        encoding="utf-8",
    )
    return zip_path


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    FONTS.mkdir(parents=True)
    SPECIMEN.mkdir(parents=True)
    DOCS.mkdir(parents=True)
    SOURCE.mkdir(parents=True)
    work = ROOT / "tmp" / "base-meridion-english-inter-work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    font_paths = [build_style(style, work) for style in STYLES]
    write_css()
    write_specimen()
    write_docs(font_paths)
    shutil.copy2(__file__, SOURCE / "build_base_meridion_english_professional.py")
    write_hashes()
    package = package_zip()
    print(f"Built {FAMILY} {VERSION}")
    print(f"Package: {package}")
    print(f"Fonts: {FONTS}")


if __name__ == "__main__":
    main()
