# BASE Meridion Kurdish design source record

- Family name: **BASE Meridion Kurdish** (typographic family, name ID 16, identical across all four weights).
- Weights: Regular 400, Medium 500, SemiBold 600, Bold 700 (name ID 17 sub-styles).
- Version: 1.013.
- Kurdish design target: `letter fixing.pdf`, supplied by the user (Adobe Illustrator artwork).
- Isolated Kurdish letters and the shown symbols (including `-` and `_`) follow the PDF vector design;
  v1.013 corrects ڵ/ڕ and brings every م form - isolated included - onto one canonical
  head size, weight and connector band.
- **Smooth/flowing joined text.** Connected word forms use the smooth, elegant base shapes so running
  Kurdish reads with a soft naskh flow (matching the reference the user supplied), rather than the
  geometric PDF outlines. Single/isolated letters still show the PDF design.
- Latin A-Z and a-z intentionally render as period dots per the user's request.

## What changed
- **Naming fixed (1.003).** The visible/typographic family is now exactly `BASE Meridion Kurdish`. Regular /
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
