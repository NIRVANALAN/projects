# Holo4D demo video — production brief for Codex (Civo)

Goal: a ~2:15 overview video in the style of the Vista4D demo
(https://media.githubusercontent.com/media/Eyeline-Labs/Vista4D/website/media/vista4d.mp4,
170 s, 1920×1080): title card → teaser → method → results → baselines → end card.
Ours leads with the persistent 3D-track visualization (source with track
overlay → 3D trajectories → projected track condition → Holo4D output with track
overlay), which is the clearest picture of the method.

**Do not commit, push, or upload anything.** Prepare everything in a staging
folder on Civo and report back (see "Report back"). The page side is wired up
separately once the media is reviewed.

## Ground rules

- Real outputs only. Every frame of a result comes from an archived Holo4D
  inference output (the step-19,500 model unless a shot says otherwise). No
  re-generated, cherry-composited or retouched results. Never show a baseline
  output that wasn't produced by that baseline's own pipeline for the same
  source clip and target trajectory.
- Never modify an inference output in place. All crops, labels, overlays and
  re-timings are written to new files under the staging root.
- Claims in on-screen text must come from the camera-ready paper. Do not add
  speed or metric claims. If a claim is needed but uncertain, leave a
  `TODO(claim)` card and list it in the report.
- Track overlays: reuse the existing page visualization exactly (persistent
  per-identity colors, the same tail length and dot style as
  `filtered20261011_v2/**/overlay.mp4` / `interleaved.mp4`, and the same jitter
  filter v2). Do not recolor tracks. Overlays on generated RGB are
  post-generation display tracks; label them "tracks (visualization)" wherever
  they appear on a generated video, never "model input".
- Pacing: 16 fps sources are placed on a 30 fps timeline by frame repetition
  (nearest frame). No optical-flow or AI frame interpolation.
- Each result shot plays at least 2 full loops (ping-pong allowed: 0..48, 47..1).

## Output spec

- Master: 1920×1080, 30 fps, H.264 High, yuv420p, CRF 16, `-movflags +faststart`,
  `holo4d_demo_master.mp4`.
- Web: same picture, CRF 23, target ≤ 60 MB, `holo4d_demo_web.mp4`, plus
  `holo4d_demo_web_poster.jpg` (title card frame, 1280 px, q85).
- Audio: none in the video files. If you propose music, deliver it separately
  as `music_suggestion.txt` (title, license URL); do not mux it.
- `captions.srt` with every on-screen text card, for accessibility.
- `contact_sheet.png`: one frame every 4 s, 6 columns.

## Visual style (match the project page and the camera-ready figures)

- Background white `#ffffff`; text `#222222`; secondary text `#666666`.
- Font: Lato (Regular 400 / Bold 700). If not installed, use the TTFs from
  Google Fonts (OFL); fall back to DejaVu Sans only if unavailable, and say so.
- Colors carry meaning, as in the overview figure: source = red `#b23a2f`,
  Holo4D output = blue `#1772d0`. Baselines in neutral dark gray `#444444`.
- Panel labels: a small rounded chip at the top-left of each panel, 26 px Bold,
  white text on `#111111e6` (source, condition, baselines) or on `#1772d0`
  (Holo4D, labelled "Holo4D (ours)"). Same wording as the page:
  "Source video", "3D track condition", "Holo4D (ours)", "Vista4D".
- Section cards: "Holo4D" wordmark 64 px Bold at top, section name 40 px
  below (e.g. "Method", "Robotics from new viewpoints", "Comparison to
  baselines"), 1.0–1.5 s, cut (no fancy transitions). Cross-fades ≤ 8 frames.
- One caption line per results shot, bottom center, 28 px, `#444444`, at most
  ~110 characters.
- Panels: 8 px gaps, 6 px corner radius, no drop shadows, no burned-in
  monospace debug text (crop it away; the existing composites have small
  "frame N / all panels synchronized" strips — exclude them).
- Safe area: keep text ≥ 64 px from frame edges.

## Shot list (target timings; ±20% is fine)

| # | Time | Shot | Content |
|---|---|---|---|
| 0 | 0:00–0:05 | Title | "Holo4D" (Bold, large); subtitle "Holistic 4D Reconstruction as Geometric Control for Video Diffusion"; authors with superscripts and affiliations as on the page; "NeurIPS 2026". White background. |
| 1 | 0:05–0:20 | Teaser mosaic | 3×2 grid at 1920×1080 of the six teaser results (`teaser/0N_*/clean.mp4`, ping-pong), each with its source clip as an inset (top-right, 34% width, white 3 px border) exactly like the page teaser. Chip "Holo4D" on each tile, "Source" on each inset. Caption: "One source video. Persistent 3D tracks. New viewpoints." |
| 2 | 0:20–0:28 | Section card | "Method" |
| 3 | 0:28–0:55 | Persistent tracks, step by step | One clip, four beats, same scene throughout (pick the clearest: Figure humanoid `figure_0__window00__start00000` with `subject_orbit_zoom`, or the man-smoking DAVIS/native clip used in the overview figure if its assets exist). (a) Source video with source-view track overlay (2D projections of the persistent 3D tracks on the source frames) — caption "4D reconstruction recovers persistent 3D trajectories". (b) The 3D trajectories in 3D: a slow orbit render of the colored track point cloud with short tails (reuse the overview-figure trajectory render if available; otherwise render with the existing visualization code — report which script). Caption "Each track keeps its identity, geometry and source color". (c) Projected into the target camera: the "3D track condition" panel — caption "Projected into the requested camera as the track condition". (d) Holo4D output, alternating clean ↔ with tracks (visualization) — caption "Holo4D generates the scene from the new camera path". |
| 4 | 0:55–1:05 | Overview figure | The camera-ready Fig. 2 (`holo4d/static/images/pipeline.webp` in the projects repo, 2928×942, or render `holo4d_final_overview.pdf` if you have it) shown full-width, with three soft highlight boxes appearing in sequence: 4D reconstructor → track condition + track encoder → DiT (width concat, channel concat of T, camera features C). 2–3 s per highlight. Caption from the paper caption, shortened. |
| 5 | 1:05–1:08 | Section card | "Robotics from new viewpoints" |
| 6 | 1:08–1:30 | Robot pairs | 3 shots, one per pair already on the page: Figure `figure_0` (subject_orbit_zoom / slow_crane_dolly_in), Tesla `tesla_0__window02__start00048` (close_crane_above / left_front_zoom), DROID GuptaLab (static_left_front / static_right_front). Layout per shot: left = source video (red chip), right = two Holo4D outputs for the two camera paths side by side (blue chips with the camera path name), each alternating clean ↔ tracks (visualization). Same source clip on both sides — never pair different recordings. Caption: "Same robot recording, two virtual camera paths". |
| 7 | 1:30–1:33 | Section card | "Video reshooting" |
| 8 | 1:33–1:50 | Natural videos | 3 shots from the page's reshooting pairs: camera-lens (crane-zoom / side-full), golf (dolly-out / dolly-in), DAVIS bear (pan_right / pan_left). Same layout as shot 6. |
| 9 | 1:50–2:00 | Long videos | Figure `figure_1` pair: source | generated continuation, both camera paths, chunk boundaries indicated by a small "chunk 1 / 2 / 3" chip (no yellow separators). Caption "Continued beyond a single 49-frame chunk". |
| 10 | 2:00–2:03 | Section card | "Comparison to baselines" |
| 11 | 2:03–2:20 | Baselines | 3 shots from the nine matched comparisons (golf/dolly-out, drive-desert/side-fly, snow-dog/crane-above): Source video | Holo4D (ours) | Vista4D, equal size, one row, labels as on the page. Include other baselines (e.g. ReCamMaster, TrajectoryCrafter, GEN3C) ONLY if matched outputs for the same source and target trajectory already exist in the archive — list what you found; do not run new baselines. Caption: "Same source video and requested camera trajectory". No "better than" wording. |
| 12 | 2:20–2:30 | End card | "Holo4D" wordmark, title, authors/affiliations, "Project page: nirvanalan.github.io/projects/holo4d", a QR code to that URL (black on white, ≥ 220 px), "Paper · Code (coming soon)", small acknowledgment line as on the page. |

If a shot's assets do not exist or look bad, substitute the closest same-kind
example and say why in the report. Keep total length 2:00–2:40.

## How to build it

- One reproducible script, `build_demo.py` (or `.sh`), driven by a
  `shotlist.yaml` that names every input file, crop rectangle, timing, label
  and caption. Title/section cards rendered from HTML (headless Chromium) or
  PIL; composition via ffmpeg filter graphs or PIL/moviepy — your choice, but
  rerunning the script must reproduce the video byte-for-byte or near it.
- Render each shot to `shots/NN_name.mp4` first (1920×1080, 30 fps, CRF 16),
  then concatenate. Keep intermediate per-shot files.
- Run CPU-heavy rendering on a compute node, not the login node.

## Staging layout

```
/scratch/shared/engs2907/open-source/holo4d/demo_video_<YYYYMMDD>/
  README.md                 what is here, how to rebuild
  shotlist.yaml
  build_demo.py
  shots/NN_name.mp4         per-shot renders
  cards/*.png               rendered title/section/end cards
  final/holo4d_demo_master.mp4
  final/holo4d_demo_web.mp4
  final/holo4d_demo_web_poster.jpg
  final/captions.srt
  final/contact_sheet.png
  manifest.json             see below
```

`manifest.json`: for every shot, the list of input files with absolute path,
sha256, kind (`source`, `holo4d_output`, `track_overlay`, `track_condition`,
`trajectory_3d_render`, `baseline:<name>`, `card`), scene id, target
trajectory id, model checkpoint/step, geometry backend (VGGT-Omega+CoWTracker /
4RC), and the exact script + command that produced any derived file
(overlays, 3D renders, crops).

## Report back (paste to Yushi; nothing is pushed)

1. Staging root path, final file sizes, duration, ffprobe line for both MP4s.
2. The shot table with what was actually used per shot (scene, trajectories,
   source/target video paths, overlay/condition paths) and any substitutions.
3. Every visualization script used, with repo path and commit: source-view
   track overlay, 3D trajectory render, track-condition render, post-generation
   overlay, interleave, and the demo builder itself — plus the exact commands.
4. Which baselines had matched outputs, and their paths.
5. Any `TODO(claim)` cards and open questions.
6. Contact sheet path.

## Lessons from the submission demo (`holo4d-nips26-demo.pptx`, Aug 2026)

Its 20 slides: logo title → "More results / in the wild" (6 × Source | Predicted, 512×288) → "Geometric camera
condition" (2 debug grids) → "Novel-view RGB and depth, iPhone" (3 × 3-row grids) → "Novel-view RGB, DAVIS"
(3 × Source + GT over a 6-method grid) → "Thanks for watching!". Clips are 4.1 s. Results there are from old
checkpoints (e.g. `14b_softsplat_step-3000`) — do not reuse them as results.

Keep:
- **Logo title card** (now `holo4d/static/images/logo.png`, transparent, 1200×360) — open and close the film with it.
- **Multi-baseline grid** on the same source and trajectory: Holo4D | ReCamMaster | GEN3C / TrajectoryCrafter | EX-4D
  | Vista4D, with the source (and, where it exists, reprojected GT) above. Matched outputs exist for the three
  comparison cases (see the handoff's baseline table) — this is stronger evidence than Holo4D vs Vista4D alone.
- **Depth alongside RGB** (iPhone rows): shows geometric consistency, which is the paper's point. Use only where
  matched depth for every method exists.
- Simple **section cards** between parts.

Avoid (the old deck did these):
- Debug grids with monospace labels, |pred − gt| heat maps, valid masks and full prompts burned into the frame.
- Calling the reprojected source "GT" (label it "Reprojected source"), white frames around letterboxed clips, and
  tiny method labels under 2×3 grids — use the page's chip labels, Holo4D (ours) in blue.
