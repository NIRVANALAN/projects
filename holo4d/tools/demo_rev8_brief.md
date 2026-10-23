# Holo4D demo film — revision 8 brief (tighter, robot-first, readable)

Base: r7 (`demo/holo4d_demo_2026-10-18-r7.mp4`, 2:27.5, 1920×1080, 30 fps). Rendering scripts and data as in
`demo_rev6_brief.md` (`/scratch/shared/engs2907/open-source/holo4d/opus_method_video_20261018/scripts/`).
Keep every global rule of rev 6 (fonts, colours, j-time base, real data only, white = exact 255) unless changed here.
Stage only: no HF upload and no page edit until local Opus approves; publish under a NEW name
(`demo/holo4d_demo_2026-10-2X-r8.mp4`) with a matching `holo4d_demo_r8.vtt`.

## What is wrong with r7 (measured on the published file)

| # | Time | Problem |
|---|---|---|
| 1 | 2.5–30.5 | Hero and grid feature DAVIS camel. The author does not want the camel. Its orbit output (17.5 s) shows a second brown camel filling the foreground. |
| 2 | 5.5–10.5, 22–25.5 | The scaffold renders are mostly black. In the grid's reconstruction stage (24 s), each cell's point cloud is a fragment filling under 15% of the cell. It reads as broken, not as "4D reconstruction". |
| 3 | 30.5–55.7 | The method animation fills 45% of the frame (content bbox x 48–1625, y 162–758). It is pinned top-left, the bottom 30% is empty, and "How it works" is 13 px. It runs 25 s. |
| 4 | 55.7–147 | Section tags ("ROBOTICS", "VIDEO RESHOOTING", …) have a 26 px cap height and sit in the corner. Panel chips are ≈ 26 px and bottom captions ≈ 28 px. At the page's ≈ 1040 px display width these become 14–15 px, which is unreadable. |
| 5 | 55.7–92 | Portrait robot rows use ≈ 55% of the frame height, so the panels are small with large white margins. |
| 6 | whole | 2:27 with no hook. The first 2.5 s are a title card, and the first result appears only at 14 s. |

## Target structure (≈ 1:40 total)

| Section | Time | Content |
|---|---|---|
| H. Hook | 0.0–4.0 | Full-bleed result, no title. The Figure humanoid `subject_orbit_zoom` output (portrait, centred, height 1080) between its source (left) and its condition (right), like the project-page player. One clean loop at 16 fps, then the matched track-overlay loop over the last 1.0 s. No text except a small "Tracks (visualization)" chip while tracks show. |
| 0. Title | 4.0–6.0 | rev 6 title card, 2.0 s, cross-fade in and out. |
| A. Hero walk-through | 6.0–19.0 | rev 6 section A with hero = DROID GuptaLab `static_right_front` (landscape; the arm is clearly visible). Stage times scaled: A1 2.5 s, A2 4.5 s, A3 2.5 s, A4 3.5 s. |
| B. Grid | 19.0–30.0 | rev 6 section B, but the eight outer cells contain no DAVIS camel and no DAVIS case at all. Use: DROID RAD static_right, DROID TRI safe_near_orbit, golf dolly-out, camera-lens crane-zoom, friends-restaurant side-dolly, fashion-walk arc-left-right, drive-desert side-fly, snow-dog crane-above. Stages 2.5 / 3.0 / 2.5 / 3.0 s. |
| M. How it works | 30.0–48.0 | Method animation re-laid out (see M), 18 s. |
| R. Robots | 48.0–72.0 | Figure, Tesla, DROID GuptaLab, 8 s each (clean loop, then track-overlay loop), larger panels (see R). |
| V. Reshooting | 72.0–84.0 | Two cases only: golf (dolly-out, dolly-in) and breakdance flare (orbit right, pan left), 6 s each. Drop camera lens. |
| L. Long videos | 84.0–92.0 | The two-chunk humanoid case, shortened to one play-through (8 s). |
| C. Baselines | 92.0–100.0 | Two cases only: golf dolly-out and snow-dog crane-above, 4 s each. |
| E. End card | 100.0–105.0 | As r7, with the rev 6 §D text sizes. |

## Fixes per section

A2/B2, the scaffold render (problem 2):
- Use the same renderer, but frame the fly-through so the point cloud fills the panel. At the source pose the render must match the source framing, which r7 already does. While flying, the target camera's look-at point = the median of the valid points at frame j, and its distance is clamped so the projected bounding box of the valid points covers ≥ 55% of the panel area.
- Final pose = the exact target pose; do not change it.
- Render splats with radius ≥ 2.5 px at 1080p, before the 2× downsample. Use background #111111.
- QA: plot the fill fraction for every frame of A2 and of each B2 cell. Every frame must be ≥ 40%. If a cell cannot reach that, the likely cause is the intrinsics: check that K is rescaled from 672×384 to the cell size.

M, method animation (problem 3):
- Centre the whole diagram and scale it so its bounding box is ≥ 1700 px wide, vertically centred, with ≥ 90 px margins.
- Stage title above the diagram: Lato Bold 52 px with a Regular 32 px suffix.
- Delete the small "How it works" label; it becomes a 1.0 s section card with "How it works" in Lato Bold 64 px, centred.
- 18 s total: drop the hold between "4D scaffold" and "video diffusion".
- Keep the track-overlay step titled "Tracks · visualization only".

R / V / L / C, readable layout (problems 4 and 5):
- Section card before each section (0.8 s, white): word Lato Bold 64 px #222, one line below Lato Regular 34 px #6B6B6B.
  - Robots: "Robots · same recording, new camera paths"
  - Video reshooting: "Video reshooting · one source, two camera paths"
  - Long videos: "Long videos · chunk-by-chunk continuation"
  - Baselines: "Comparison · same source and target camera"
- Remove the corner tags.
- Panel chips: Lato Bold 34 px, padding 8×14 px. Bottom captions: Lato Regular 36 px. Minimum rendered cap height 24 px for any text (measure it).
- Portrait rows: panels 900 px tall (was ≈ 600), three across with 40 px gaps, centred. Landscape pairs: two 900×506 panels side by side, with the source as a 480×270 inset above them, centred.
- Baseline grid: 2×3 cells of 600×338, with 12 px gaps.

## QA (report all)

1. ffprobe line, total length (target 1:40 ± 5 s), file sizes of master and web encodes.
2. Full-resolution PNGs at 1, 3.5, 5, 8, 10, 12, 16, 18, 21, 24, 27, 29, 33, 40, 46, 50, 58, 75, 88, 95, 102 s.
3. The A2 and B2 fill-fraction plots (problem 2).
4. Smallest rendered glyph cap height per section.
5. A list of every case used: case id, trajectory, backend, step, source/pred/npz paths. Confirm that no DAVIS camel frame appears anywhere.
6. White regions ≥ 99.5% exact 255.
