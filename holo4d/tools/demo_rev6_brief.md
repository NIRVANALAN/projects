# Holo4D demo film — revision 6 brief (Vista4D-style opening)

Reference: Vista4D demo, https://media.githubusercontent.com/media/Eyeline-Labs/Vista4D/website/media/vista4d.mp4,
0:00–0:32. Watch it frame by frame first. What makes it work: ONE clip is walked through the pipeline inside ONE
framed panel that never cuts; the 4D-reconstruction stage shows the point cloud while the virtual camera FLIES from
the source viewpoint to the target viewpoint; then the panel shrinks into the centre of a 3×3 grid where eight other
scenes go through the same stages in sync.

Scope: replace rev 5's opening (title card 0:00–0:03 + results mosaic 0:03–0:17) with sections 0, A and B below.
Everything after it (method animation, robots, reshooting, long videos, baselines, end card) stays as in rev 5,
except the end-card text sizes in D. Stage only: no HF upload, no page edits, until local Opus approves.

## Global rules

- 1920×1080, 30 fps, H.264 yuv420p, faststart, CRF ≈ 20 master / ≈ 23 web. White background is exactly RGB 255.
- Lato (Regular / Bold). Primary text ≥ 44 px, secondary text ≥ 28 px (the page shows the film ~1040 px wide, so
  1080p text shrinks to 54%). Measure rendered glyph heights in QA; do not trust font-size alone.
- Colours: source red #B03A2E, reconstruction/condition blue #2B5D9B, Holo4D (ours) blue #1772d0, ink #222222,
  muted #6B6B6B.
- Time base: every panel shows the same source frame index j at the same moment. j advances at 16 fps (nearest-frame
  mapping to 30 fps, no interpolation) and ping-pongs 0..48..1 so it never jumps.
- Real data only: final model (step 19,500), each case's own reconstruction, condition and target trajectory — the
  exact run that produced the generated video shown.
- Cross-fades 0.4–0.6 s, ease-in-out. No zooms or pans of the whole frame.

## 0. Title card (0.0–2.5 s)

`holo4d/static/images/logo.png` (transparent, 1200×360) scaled to 960 px wide, centred, top at y≈300. One line below
at y≈720: "Holistic 4D Reconstruction as Geometric Control for Video Diffusion", Lato Regular 60 px, #222, centred.
Nothing else (no authors, affiliations, venue, rule — the page shows them right above the film; the end card keeps
them). Fade in 0.4 s; at 2.1 s cross-fade into A1.

## A. Hero walk-through (2.5–18.0 s)

One panel 1280×720 at (320, 250) (bottom edge y = 970), frame border 8 px drawn just outside the panel, square
corners. Stage title centred above the panel, baseline at y≈205: big word Lato Bold 56 px in the stage colour + a
space + small suffix Lato Regular 30 px #6B6B6B (like Vista4D's "4D reconstruction  to obtain a 4D point cloud").
When the stage changes, the frame colour and title cross-fade over 0.4 s; the panel itself never cuts.

Hero case: a landscape case with clear object/robot motion. Recommended DROID · GuptaLab · static_left_front
(alternatives: DAVIS camel orbit_left, kite-surf pan_left). Not man-smoke (the method animation uses it).

| Stage | Time | Title (word + suffix) | Frame colour | Panel content |
|---|---|---|---|---|
| A1 | 2.5–5.5 | Source video · as input | #B03A2E | source_rgb, j advancing |
| A2 | 5.5–10.5 | 4D reconstruction · persistent 3D trajectories | #2B5D9B | see A2 |
| A3 | 10.5–13.5 | Track condition · at the target camera | #2B5D9B | see A3 |
| A4 | 13.5–18.0 | Holo4D · output | #1772d0 | see A4 |

A2 — the key shot (5.5–10.5 s):
1. 5.5–6.1: cross-dissolve from the source video to the scaffold rendered FROM THE SOURCE CAMERA at the same j. Because
   the render matches the source framing, it reads as the video turning into a point cloud.
2. 6.1–7.0: hold at the source camera (j keeps advancing).
3. 7.0–10.0: the render camera flies from the source pose to the target pose (ease-in-out), j keeps advancing.
4. 10.0–10.5: hold at the target pose.

Renderer (extend `render_teaser3d_video.py` / the dump_scene data, scripts in
`/scratch/shared/engs2907/open-source/holo4d/opus_method_video_20261018/scripts/`):
- Points: all valid identities at frame j (`tracks_world_native[:, j]`), source colours (query-frame RGB), z-buffered
  splats whose size grows as points come closer (as `track_style.condition_filled`), on a dark background #111111.
- Trails: sparse foreground identities on the 14-px query grid, last 12 frames, turbo colours as in
  `render_teaser3d.py`, 2–3 px, heads 4 px.
- Camera at blend weight w(t): rotation = slerp(R_src[j], R_tgt[j], w) (scipy Rotation), position = lerp(c_src[j],
  c_tgt[j], w), intrinsics K = lerp(K_src[j], K_tgt[j], w) rescaled from 672×384 to 1280×720. OpenCV pinhole.
  Source poses `camera_c2w_native` + `intrinsics`; target poses/intrinsics = the run's effective target camera
  (`tgt_<traj>` / `K_<traj>` from dump_scene for native110; for DROID/DAVIS read them from the exact condition used at
  sampling — do not re-estimate).
- Render at 2× and downsample (no aliasing); 30 fps.

A3 (10.5–13.5): at the target pose, cross-fade 0.6 s from the A2 render into `track_style.condition_filled(S, j,
bg=(17,17,17))` frames upscaled to 1280×720 — same view, so only the look changes (splats close into surfaces;
trails fade out).

A4 (13.5–18.0): cross-fade 0.6 s into the generated video (clean) at the same j; at 16.0 s cross-fade to the track
overlay for 2 s with a chip "Tracks (visualization)" (bottom-right, 28 px, white on #000000c0).

## B. Grid (18.0–31.5 s)

- 18.0–19.0: the hero panel (and its frame) scales from 1280×720 at (320,250) to the centre cell 640×360 at (640,360);
  the frame thins to 0; the eight outer cells fade in during the move. The grid fills the whole 1920×1080 frame:
  3×3 cells of 640×360, no gaps, no per-cell labels.
- Outer cells: eight other landscape cases, for example DROID RAD static_right, DROID TRI (approved trajectory),
  DAVIS camel orbit_left, DAVIS kite-surf pan_left, golf dolly-out, camera-lens crane-zoom, breakdance-flare
  orbit_right, drive-desert side-fly. Each needs source_rgb, pred_rgb, its reconstruction (dump_scene-style npz) and
  its effective target camera.
- Centre cell after the move: white, showing the current stage name centred (word 52 px Bold in the stage colour,
  suffix 28 px #6B6B6B on a second line).
- All eight cells advance through the same four stages in sync:

| Stage | Time | Cells | Centre text |
|---|---|---|---|
| 1 | 19.0–22.0 | source video | Source video / as input (red) |
| 2 | 22.0–25.5 | scaffold render, source→target fly-through over 2.5 s | 4D reconstruction / persistent 3D trajectories (blue) |
| 3 | 25.5–28.0 | condition_filled at the target camera | Track condition / at the target camera (blue) |
| 4 | 28.0–31.5 | Holo4D output (clean) | logo.png, 520 px wide |

Cross-fade 0.4 s at each stage boundary; then cut to the method animation.

## C. Rest of the film

Unchanged from rev 5 (method animation centred on white, robots, reshooting, long videos, baselines, end card).

## D. End card

Keep layout; authors ≥ 36 px, affiliations ≥ 30 px, "NeurIPS 2026" ≥ 44 px, acknowledgments ≥ 28 px, QR ≥ 260 px.

## QA (report all of these)

1. Web MP4 path + ffprobe line; total length.
2. Full-resolution PNGs at 1, 4, 6, 7.5, 9, 10.3, 12, 15, 17, 18.5, 20, 23.5, 27, 30 s.
3. Alignment checks: (a) A2 first render frame vs the source frame at the same j — side-by-side + 50% blend PNG
   (should line up); (b) A2 last render frame vs the condition frame at the same j (same view).
4. Per-case table: case id, trajectory, source/pred/npz paths, which geometry backend, target-camera source.
5. White ≥ 99.5% exact 255 in white regions; measured glyph heights of the smallest text in sections 0, A, B, D.
6. Stage only; local Opus approves before HF upload under a NEW file name (e.g. demo/holo4d_demo_2026-10-19.mp4).
