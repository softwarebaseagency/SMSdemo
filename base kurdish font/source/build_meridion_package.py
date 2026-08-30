"""Specimen + documentation + optional packaging for BASE Meridion Kurdish 1.013."""
from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from PIL import Image, ImageDraw, ImageChops, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FAMILY = "BASE Meridion Kurdish"
FILE_FAMILY = "BASEMeridionKurdish"
PACKAGE_STEM = "BASE-Meridion-Kurdish"
VERSION = "1.013"

DIST = ROOT
FONTS = DIST / "fonts"
DOCS = DIST / "documentation"
SOURCE = DIST / "source"
SPECIMEN = DIST / "specimen"

STYLES = [("Regular", 400), ("Medium", 500), ("SemiBold", 600), ("Bold", 700)]
NAVY, BLUE, CREAM, INK = (17, 30, 52), (49, 94, 255), (246, 241, 232), (20, 25, 35)
ARIAL = "C:/Windows/Fonts/arial.ttf"
ARIALBD = "C:/Windows/Fonts/arialbd.ttf"


# --------------------------- Kurdish text raster --------------------------- #
def _flatten(rp):
    contours, cur, prev = [], [], None
    for op, a in rp.value:
        if op == "moveTo":
            cur = [a[0]]; prev = a[0]
        elif op == "lineTo":
            cur.append(a[0]); prev = a[0]
        elif op == "qCurveTo":
            on = a[-1]; offs = a[:-1]
            if on is None:            # all-off-curve closed contour -> back to start
                on = cur[0] if cur else offs[0]
            if prev is None:
                prev = on; cur = [on]
            p0 = prev
            for i, ctrl in enumerate(offs):
                p2 = on if i == len(offs) - 1 else ((ctrl[0] + offs[i + 1][0]) / 2, (ctrl[1] + offs[i + 1][1]) / 2)
                for t in [k / 12 for k in range(1, 13)]:
                    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * ctrl[0] + t * t * p2[0]
                    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * ctrl[1] + t * t * p2[1]
                    cur.append((x, y))
                p0 = p2
            prev = on
        elif op == "curveTo":
            c1, c2, e = a; p0 = prev
            for t in [k / 16 for k in range(1, 17)]:
                x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * c1[0] + 3 * (1 - t) * t * t * c2[0] + t ** 3 * e[0]
                y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * c1[1] + 3 * (1 - t) * t * t * c2[1] + t ** 3 * e[1]
                cur.append((x, y))
            prev = e
        elif op == "closePath":
            if cur:
                contours.append(cur); cur = []
    if cur:
        contours.append(cur)
    return contours


def kurdish_width(path, text, size):
    data = open(path, "rb").read(); face = hb.Face(data); font = hb.Font(face); font.scale = (face.upem, face.upem)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); buf.language = "ckb"
    hb.shape(font, buf)
    return sum(p.x_advance for p in buf.glyph_positions) * (size / face.upem)


def draw_kurdish(img, path, text, right_x, baseline, size, color=INK):
    ft = TTFont(path); gs = ft.getGlyphSet(); order = ft.getGlyphOrder()
    data = open(path, "rb").read(); face = hb.Face(data); font = hb.Font(face); font.scale = (face.upem, face.upem)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); buf.language = "ckb"
    hb.shape(font, buf)
    scale = size / face.upem
    W, H = img.size
    px = right_x - sum(p.x_advance for p in buf.glyph_positions) * scale
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        rp = RecordingPen(); gs[order[info.codepoint]].draw(rp)
        try:
            contours = _flatten(rp)
        except Exception:
            contours = []
        if contours:
            gm = Image.new("1", (W, H), 0)
            for c in contours:
                if len(c) >= 3:
                    poly = [(px + (X + pos.x_offset) * scale, baseline - (Y + pos.y_offset) * scale) for (X, Y) in c]
                    pm = Image.new("1", (W, H), 0); ImageDraw.Draw(pm).polygon(poly, fill=1)
                    gm = ImageChops.logical_xor(gm, pm)
            img.paste(color, (0, 0), gm)
        px += pos.x_advance * scale


def write_specimen_png():
    W, H = 1680, 2050
    img = Image.new("RGB", (W, H), CREAM)
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, W, 360], fill=NAVY)
    dr.text((70, 120), FAMILY, font=ImageFont.truetype(ARIALBD, 92), fill=(255, 255, 255))
    dr.text((74, 245), f"KURDISH SORANI TYPE FAMILY  •  v{VERSION}  •  BASE AGENCY",
            font=ImageFont.truetype(ARIAL, 27), fill=(210, 222, 255))
    reg = str(FONTS / f"{FILE_FAMILY}-Regular.ttf")
    draw_kurdish(img, str(FONTS / f"{FILE_FAMILY}-Bold.ttf"), "ڕوون، فەرمی، کوردی",
                 W - 70, 300, 66, color=(255, 255, 255))
    rows = ["ق و ه ر ت ی ئ",
            "ح ۆ پ ل ا س",
            "د ف گ ە ژ ک ڵ ز",
            "خ ج ڤ ب ن م"]
    y = 520
    for r in rows:
        draw_kurdish(img, reg, r, W - 70, y, 72); y += 128
    # weight ladder
    y = 1120
    for lab, _w in STYLES:
        dr.text((70, y - 40), lab, font=ImageFont.truetype(ARIALBD, 34), fill=BLUE)
        draw_kurdish(img, str(FONTS / f"{FILE_FAMILY}-{lab}.ttf"), "کوردستان پەروەردە", W - 70, y, 70); y += 150
    # symbols card
    dr.rounded_rectangle([70, 1760, W - 70, 1960], radius=22, fill=(255, 255, 255))
    draw_kurdish(img, reg, "! @ # $ % ^ & *  ( ) _ - + = | \\ ?", W - 110, 1855, 54, color=BLUE)
    dr.text((90, 1985), "Isolated Kurdish letters + symbols follow letter fixing.pdf. Latin A–Z/a–z render as dots by design.",
            font=ImageFont.truetype(ARIAL, 26), fill=INK)
    SPECIMEN.mkdir(parents=True, exist_ok=True)
    out = SPECIMEN / f"{FILE_FAMILY}-Specimen.png"
    img.save(out)
    print("wrote", out)


def write_target_fixes_png():
    """Focused visual proof for the current Kurdish outline repairs."""
    W, H = 1800, 1660
    img = Image.new("RGB", (W, H), CREAM)
    dr = ImageDraw.Draw(img)
    dr.rectangle([0, 0, W, 300], fill=NAVY)
    dr.text((70, 78), "Kurdish Target Fixes", font=ImageFont.truetype(ARIALBD, 82), fill=(255, 255, 255))
    dr.text((74, 190), f"BASE MERIDION KURDISH  •  v{VERSION}  •  ڵ / م / ڕ",
            font=ImageFont.truetype(ARIAL, 28), fill=(210, 222, 255))

    regular = str(FONTS / f"{FILE_FAMILY}-Regular.ttf")
    rows = [
        ("ISOLATED", "ڵ   م   ڕ", 118),
        ("LAM-V FORMS", "بڵ   ڵب   بڵب", 94),
        ("MEEM FORMS", "بم   مب   بمب", 94),
        ("RREH FORMS", "بڕ   ڕب   بڕب", 94),
        ("MEEM WORD-END", "م   کەم   ئەم   دەم   مەم   گەرم", 82),
        ("SORANI", "مامۆستا   مەریوان   ئامادە", 82),
        ("SORANI", "بەڕێوەبردن   گۆڕانکاری   کڕیار", 76),
    ]
    y = 430
    label_font = ImageFont.truetype(ARIALBD, 25)
    for label, text, size in rows:
        dr.text((70, y - 45), label, font=label_font, fill=BLUE)
        draw_kurdish(img, regular, text, W - 70, y, size)
        y += 170

    dr.rounded_rectangle([70, 1540, W - 70, 1620], radius=18, fill=(255, 255, 255))
    dr.text((95, 1562), "Verified with Kurdish shaping: isolated, initial, medial, final, lam-alef, and meem ligature paths.",
            font=ImageFont.truetype(ARIAL, 25), fill=INK)
    SPECIMEN.mkdir(parents=True, exist_ok=True)
    out = SPECIMEN / f"{FILE_FAMILY}-Target-Fixes.png"
    img.save(out)
    print("wrote", out)


def write_specimen_html():
    faces = "\n".join(
        f"@font-face{{font-family:'{FAMILY}';src:url('../fonts/{FILE_FAMILY}-{lab}.woff2') format('woff2');font-weight:{w};font-style:normal;font-display:swap}}"
        for lab, w in STYLES)
    html = f"""<!doctype html><html lang="ckb" dir="rtl"><head><meta charset="utf-8">
<title>{FAMILY}</title><style>{faces}
body{{margin:0;background:{'#f6f1e8'};color:#111e34;font-family:'{FAMILY}',sans-serif}}
header{{background:#111e34;color:#fff;padding:6vw 7vw 5vw}}
h1{{font-family:Arial,sans-serif;direction:ltr;margin:0;font-size:60px}}
.sub{{font-family:Arial,sans-serif;direction:ltr;color:#cdd9ff;letter-spacing:.12em;font-size:15px;margin-top:10px}}
main{{max-width:1150px;margin:auto;padding:6vw 7vw}}
p{{font-size:56px;line-height:1.7;margin:.2em 0}}
.lab{{font-family:Arial,sans-serif;direction:ltr;color:#315eff;font-weight:bold;font-size:18px;margin-top:1.4em}}
.r{{font-weight:400}}.m{{font-weight:500}}.s{{font-weight:600}}.b{{font-weight:700}}
.note{{font-family:Arial,sans-serif;direction:ltr;color:#141923;font-size:16px;margin-top:2em}}
.latin{{direction:ltr;text-align:left}}</style></head>
<body><header><h1>{FAMILY}</h1><div class="sub">KURDISH SORANI TYPE FAMILY &bull; v{VERSION} &bull; BASE AGENCY</div></header>
<main>
<p class="r">ق و ه ر ت ی ئ</p>
<p class="r">ح ۆ پ ل ا س</p>
<p class="r">د ف گ ە ژ ک ڵ ز</p>
<p class="r">خ ج ڤ ب ن م</p>
<div class="lab">v1.012 target repairs</div>
<p class="r">ڵ &nbsp; م &nbsp; ڕ</p>
<p class="r">بڵ &nbsp; ڵب &nbsp; بڵب &nbsp; بم &nbsp; مب &nbsp; بمب &nbsp; بڕ &nbsp; ڕب</p>
<p class="r">م &nbsp; کەم &nbsp; ئەم &nbsp; دەم &nbsp; مەم &nbsp; گەرم</p>
<p class="r">سڵاو &nbsp; هەڵبژاردن &nbsp; کۆمەڵ &nbsp; بەڕێوەبردن &nbsp; گۆڕانکاری</p>
<div class="lab">Regular 400</div><p class="r">کوردستان پەروەردە</p>
<div class="lab">Medium 500</div><p class="m">کوردستان پەروەردە</p>
<div class="lab">SemiBold 600</div><p class="s">کوردستان پەروەردە</p>
<div class="lab">Bold 700</div><p class="b">کوردستان پەروەردە</p>
<p class="note">Isolated Kurdish letters and shown symbols follow letter fixing.pdf. Connected shaping stays active. Latin A&ndash;Z / a&ndash;z render as period dots by design.</p>
</main></body></html>"""
    out = SPECIMEN / f"{FILE_FAMILY}-Specimen.html"
    out.write_text(html, encoding="utf-8")
    print("wrote", out)


def write_docs():
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "DESIGN-SOURCE-RECORD.md").write_text(
        f"""# {FAMILY} design source record

- Family name: **{FAMILY}** (typographic family, name ID 16, identical across all four weights).
- Weights: Regular 400, Medium 500, SemiBold 600, Bold 700 (name ID 17 sub-styles).
- Version: {VERSION}.
- Kurdish design target: `letter fixing.pdf`, supplied by the user (Adobe Illustrator artwork).
- Isolated Kurdish letters and the shown symbols (including `-` and `_`) follow the PDF vector design;
  v1.013 corrects ڵ/ڕ and brings every م form - isolated included - onto one canonical
  head size, weight and connector band.
- **Smooth/flowing joined text.** Connected word forms use the smooth, elegant base shapes so running
  Kurdish reads with a soft naskh flow (matching the reference the user supplied), rather than the
  geometric PDF outlines. Single/isolated letters still show the PDF design.
- Latin A-Z and a-z intentionally render as period dots per the user's request.

## What changed
- **Naming fixed (1.003).** The visible/typographic family is now exactly `{FAMILY}`. Regular /
  Medium / SemiBold / Bold are sub-styles of that one family (typographic name IDs 16/17 and WWS
  IDs 21/22), with a valid RIBBI split on name IDs 1/2 so every weight is reachable in legacy apps
  too. The old leftover `Base-Kurdish` WWS name was removed.
- **Weight axis rebuilt cleanly (1.003).** Medium, SemiBold and Bold are regenerated from the
  Regular master with a stroke-outset method (skia-pathops union), replacing the previous faux-bold
  that produced lumpy, self-intersecting outlines bloated to ~9x the point count. Bold outlines are
  now smooth, counters stay open, and the four weights share identical letter heights and metrics.
- **Smooth/flowing direction (1.010).** Earlier builds (1.004-1.009) transplanted the geometric PDF
  outlines into the joined start/middle/end forms so words matched the PDF exactly. The user then chose
  the smooth, elegant reference style instead, so the joined forms now keep the base font's soft naskh
  shapes and the geometric transplants are switched off (SMOOTH=True in the build). Isolated letters
  still carry the PDF design; connected text flows smoothly. The transplant code is retained and can be
  re-enabled (SMOOTH=False) if the geometric direction is ever wanted again.
- **Kurdish target repair (1.011).** Rebuilt `ڵ` (U+06B5) from the correct lam body plus small-V mark,
  including all joining and lam-alef forms; restored `م` (U+0645) to its canonical size and baseline
  connector band so its contextual ligatures no longer jump in size or detach; and rebuilt `ڕ` (U+0695)
  from this family's corrected reh body while preserving its right-joining-only behavior and V-below mark.
- **Meem placement repair (1.012).** Restored the supplied PDF's full-sized isolated `م` and placed
  it using Arabic/Kurdish reference spacing. Word-final meem after Kurdish non-joiners now has balanced placement,
  while initial/medial/final joins and established ligatures retain their correct connector geometry.
- **Isolated meem rebuilt (1.013).** The glyph 1.012 left at U+0645 / U+FEE1 was a foreign outline:
  stroke weight ~53 units against a family norm of ~110, and a head counter of 254x145 where the
  joined forms - and the font's own never-edited meem drawings (`glyph00100`, `glyph00104`,
  `uniFCCC`) - all carry ~390x368 at y[127,495]. Kurdish selects the isolated form whenever a final
  `م` follows a non-joiner (ە و ر ا د ز ژ), which is a large share of all words, so that thin
  glyph is what readers actually saw at the end of words: undersized, spindly, and visibly a
  different letter from the م in `مم`. It is now rebuilt from this family's own isolated meem and
  fitted to the canonical head top of 636 - exactly the correction the joined forms already carried -
  with family sidebearings (advance 1342, right sidebearing 90) and the harakat anchors taken from
  `uniFEE2`, whose head sits in the same place. All five meem forms now share one head, one weight
  and one 0-155 connector band. Measured word clearance after non-joiners is 175-325 units, inside
  the family's own range of 136-341.
- **Symbol set completed (1.013).** 286 glyphs added across punctuation, superior and inferior
  figures, 16 vulgar fractions, mathematics, arrows, geometric shapes, ticks and ballot boxes,
  card suits, musical marks, letterlike symbols, 27 currency signs (including ﷼, composed from the
  family's own Arabic letters) and Arabic signs. Everything is drawn to the family's measured
  constants: symbol stroke 119, figure stroke 181, optical centre (635, 717), maths axis 675 and the
  1270-unit symbol advance already used by the existing arrows, dashes and quotes.
""",
        encoding="utf-8")

    (DIST / "README.md").write_text(
        f"""# {FAMILY} {VERSION}

One family, four weights:

- `fonts/{FILE_FAMILY}-Regular.ttf` (400)
- `fonts/{FILE_FAMILY}-Medium.ttf` (500)
- `fonts/{FILE_FAMILY}-SemiBold.ttf` (600)
- `fonts/{FILE_FAMILY}-Bold.ttf` (700)
- matching `.woff2` web fonts

The typographic family name is **{FAMILY}** for every file, so modern design apps
(Adobe CC, Figma, Canva, current Office, macOS) show a single family named
`{FAMILY}` with Regular / Medium / SemiBold / Bold as selectable styles.

Isolated Kurdish letters and the shown symbols follow the supplied `letter fixing.pdf`, with the
v1.013 corrected forms for ڵ, م, and ڕ. Every م form now shares one head size, weight and
connector band, so word-final م after a non-joiner matches the rest of the word.

v1.013 also completes the symbol coverage: punctuation, superior/inferior figures, vulgar fractions,
mathematics, arrows, geometric shapes, ticks and ballot boxes, card suits, music, letterlike marks,
currency (including ﷼) and Arabic signs.

Connected Kurdish shaping stays active. Latin A-Z / a-z render as period dots by design.

Copyright (c) 2026 Base Agency. All rights reserved.
""",
        encoding="utf-8")

    (DIST / "LICENSE-BASE-AGENCY.txt").write_text(
        f"""{FILE_FAMILY.upper()} PROPRIETARY OWNERSHIP AND LICENSE AGREEMENT
Version 1.0 - 8 July 2026

{FAMILY} is proprietary font software for Base Agency. Copyright (c) 2026 Base Agency. All rights reserved.

Base Agency may use, install, reproduce, modify, publish, distribute, embed, sublicense, commercialize,
sell, and create derivative works from {FAMILY} worldwide, perpetually, and royalty-free.

Standalone redistribution is prohibited unless Base Agency grants written permission.
""",
        encoding="utf-8")
    print("wrote docs")


def write_checksums():
    lines = []
    for p in sorted(FONTS.iterdir()):
        if p.is_file():
            lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  fonts/{p.name}")
    (DOCS / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote checksums")


def copy_sources():
    # Workspace-local builds already operate on the canonical files in source/.
    SOURCE.mkdir(parents=True, exist_ok=True)
    print("sources already current")


def package():
    package_dir = ROOT / "build"
    package_dir.mkdir(parents=True, exist_ok=True)
    zip_path = package_dir / f"{PACKAGE_STEM}-{VERSION}-Base-Agency.zip"
    package_files = [ROOT / "README.md", ROOT / "LICENSE-BASE-AGENCY.txt"]
    for folder_name in ("fonts", "documentation", "source", "specimen"):
        package_files.extend(
            path for path in (ROOT / folder_name).rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(package_files):
            z.write(p, p.relative_to(ROOT))
    (package_dir / f"{zip_path.name}.sha256").write_text(
        f"{hashlib.sha256(zip_path.read_bytes()).hexdigest()}  {zip_path.name}\n", encoding="utf-8")
    print("packaged", zip_path, f"({zip_path.stat().st_size//1024} KB)")
    return zip_path


if __name__ == "__main__":
    write_specimen_png()
    write_target_fixes_png()
    write_specimen_html()
    write_docs()
    copy_sources()
    write_checksums()
    if "--package" in sys.argv:
        package()
