# Holo4D project page — author requirements and refinement brief

Everything the author (Yushi) asked for while the page was redesigned on 2026-10-17/18, in one place. The live page at
`main` (the commit that added this sentence or later) implements all of it; refine it further without breaking any item below. Live:
https://nirvanalan.github.io/projects/holo4d/ · local: `cd projects && python -m http.server 8765` → `/holo4d/`.

## 0. How to work

- `git pull` first; the page is `holo4d/index.html`, `static/css/editorial.css` (last layer, wins), `static/js/gallery.js`,
  `static/js/showcase-selection.js`. Media are pinned on HF (`static/js/media-config.js`); never overwrite media.
- Check every change in a real browser at **1920, 1440 and 390 px**, by screenshot, not only assertions: no console
  errors, no horizontal scroll, nothing overlapping or clipped.
- Real outputs only. No fabricated assets, numbers or claims; claims come from the camera-ready paper
  (`overleaf/Holo4D-overleaf/sec/`).
- Commit with a clear message; push only when the author approves.

## 1. Look and feel

- **Identity = the author's homepage** (https://nirvanalan.github.io/): Lato, white background, ink `#222`,
  links `#1772d0`, hover `#f09228`, neutral greys. No green/teal. Paper colours inside figures/videos: source red
  `#B03A2E`, target/ours blue `#2B5D9B`.
- **References**: Vista4D (https://eyeline-labs.github.io/Vista4D/) is the direct competitor and the main layout
  reference (big, intuitive video cards, auto-advancing galleries); VideoMimic (https://www.videomimic.net/) for
  intuitive visualizations and **left alignment**; PersistBench (https://www.guangzhaohe.com/persistbench/) for
  calm, natural reading, the **left contents sidebar**, narrower width and the acknowledgements format;
  Academic Project Page Template and 4RC (abstract section).
- **Alignment**: everything starts at one left edge (eyebrow, heading, intro, subheading, card title, thumbnails).
  Centred section headings were rejected ("太蠢"). Only the title block (title, authors, links) is centred.
- **Width**: one content column of **1040 px** (the homepage width). "Too wide" and "margins too large" were both
  raised; 1040 px with 14–72 px gutters is the agreed balance. **Every block shares the column's left and right
  edge** (text blocks, galleries, method video, acknowledgements, concurrent works, BibTeX card, dividers); reading
  measure is controlled by font size, not by narrower boxes that end at different right edges.
- **Type = PersistBench's scale, nothing else**: 60 title, 40 subtitle, 24 section headings, 20 body/intro/abstract,
  16 UI/nav/authors/card titles/details, 14 captions/footnotes/code. One family (Lato; BibTeX monospace); form
  controls inherit it. Labels inside videos must be readable. Text never touches lines (borders, arrows).
- **Logo**: `static/images/logo.webp` (transparent; from the submission demo deck) is the page title; the favicon /
  touch icon / top-bar mark is the cube crop (`favicon.png`, `apple-touch-icon.png`); `logo.png` is the og:image.
- **Navigation**: clear and obvious. ≥ 1440 px: PersistBench-style fixed contents sidebar placed just left of the
  content column (not at the window edge); smaller screens: sticky top bar with bold 15–16 px links.

## 2. Page order

Logo (as the title, like 4RC) + subtitle, authors (linked), affiliations, NeurIPS 2026, buttons (Paper, Code →
https://github.com/NIRVANALAN/Holo4D, …) → **teaser mosaic** → 01 Robotics → 02 Video reshooting
→ 03 Long videos → 04 Baselines → **Abstract** → **Method** (animated) → Acknowledgements → Concurrent works → BibTeX.

## 3. Teaser

Six Holo4D outputs (two portrait humanoids as tall end tiles, four landscape tiles 2×2 between), each with its
**source video as a synced inset** (CAT4D/Vista4D style) so the viewer sees input and result at once. Scene name
inside the tile. No Vista4D scenes in the teaser. No redundant "Holo4D" chip on every tile. Plays only on screen.

## 4. Galleries (robots, reshooting, long videos, baselines)

- **Vista4D-style framed cards**: white card, hairline border, ~14 px radius, soft shadow; title + camera path at top.
- **Pairing**: two cards per desktop row = the **same source clip with two different camera trajectories**. Never
  pair different recordings; singletons stay hidden. **One thumbnail and one step per pair** (not per card).
- **Auto-advance** like Vista4D after the visible pair has played (twice for short clips, once for long), only while
  on screen; stops for good once the visitor clicks, swipes or uses the keyboard in that gallery.
- **Labels**: large plain chips over the panels — "Source video", "3D track condition", **"Holo4D (ours)" in blue**;
  same for baselines ("Vista4D" neutral).
- **Thumbnail strip** spans the full content width (capped thumbnails when few).
- **Consistent video size** across sections: wide composites (baselines, long manipulation) are one per row so the
  Holo4D panel is about as large as in the robot cards. Baselines show **Source | Holo4D (ours) | Vista4D**.
- Order: humanoids Figure → Tesla → Figure #1; manipulation GuptaLab → TRI → RAD → TRI near-object pair (has
  left-side artifacts) last. Long videos: one gallery, humanoid pairs first, then GuptaLab; wide strips drawn stacked.
- Section heading for comparisons is **"Baselines"** (not "vs. Vista4D").

## 5. Abstract

Camera-ready abstract verbatim (`sec/0_abstract.tex`, minus the project-page sentence), headed
"A 4D scaffold to tame video generation." — the core message is **4D as a scaffold that tames video generation**.
Key phrases in red (`.key`), short enough to wrap cleanly. Two columns on desktop (heading | text), one on mobile.

## 6. Method (animated Fig. 2)

The camera-ready Fig. 2 **builds up stage by stage** while the real case plays inside it (source video, moving
persistent 3D tracks, readable track condition, Holo4D output, visualization-only overlay); one caption per phase
right above the figure; **no panning/zooming** (rejected as dizzying). Loops while on screen. It is built and exported
**in PowerPoint** so it stays editable: deck `OneDrive …/submission-folder/holo4d-fig2-animated.pptx`, builder
`~/.claude/skills/paper-figure-style/scripts/pptx/fig2v.py`, full record `overleaf/Holo4D-overleaf/doc/demo-figure-visualization.md`.
The track condition must look like the scene seen from the new camera (surfaces + grey unseen), not abstract dots.
Further author decisions, all already in the current video:
- The **4D reconstructor** and **track encoder** glyphs show data flowing through them, **one pass each** when their
  stage appears, then rest static (reconstructor: source-red packet in → track colours out into the 3D panel;
  encoder: track colours in → grey feature tokens out into T).
- The DiT stack is labelled **"DiT block ×N"** (the block count differs between models); the paper figure keeps ×40.
- Labels never touch lines ("4D reconstructor", "Track encoder" lifted clear of the lane border and arrows).
- The slide is fitted to the figure (1920×718) so the caption sits right above it.
**Ownership**: the method video is rebuilt by local Opus with `fig2v.py` (the scripts live in the local figure skill,
not on Civo). Do not re-encode, crop or overlay `static/videos/method-overview.mp4`; send change requests instead.

## 7. Closing sections

- **Acknowledgements** (above concurrent works), PersistBench style: one paragraph, every person linked to their
  verified homepage, funding (Sony 2024, ERC CoG UNION 101001212, EPSRC EP/Z001811/1 SYN3D), Isambard-AI and Dawn AIRR.
- **Concurrent works**: Vista4D, Lyra [1, 2], Atlas — **one concise line each, including how Holo4D differs**.
- **BibTeX**: compact card sized to its content, Copy button.

## 8. Known debt / good next refinements

1. CSS is four overlapping layers (`index.css`, `polish.css`, `yushi-theme.css`, `editorial.css`) with `!important`
   fights. Consolidate into one stylesheet (start from `projects/template/static/project.css`, the homepage-style
   template) without changing the look; then delete the dead rules.
2. A full typography/spacing pass at 1440 and 390 px: equal vertical rhythm between sections; intro → media gap
   ≈ 20–24 px; no large empty bands.
3. Long videos: Figure #0, DROID RAD and DROID TRI need a second trajectory (Task C) before they can be shown.
4. The Codex demo film (`demo_video_20261017`) still has the review notes from local Opus (fill the frame, use the
   page's pairs, clean-then-tracks, crop debug text, fix overview highlights) — apply before publishing it.
