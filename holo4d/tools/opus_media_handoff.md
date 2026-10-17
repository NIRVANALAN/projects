# Opus media handoff — 2026-10-17

Tasks A and B are ready. Optional Task C is deferred; no new long-path diffusion job was submitted.

## Pin and scope

HF repo: `yslan/Holo4D-2026`; revision **`9778c4cc4adbb7d5c50fa5edae57f8bca2581bf1`**.
Prefix: `project_page/media_20261012/`.
Added exactly30 files (15 MP4 +15 JPEG), 9,222,071bytes. The previous406 assets retain their original blob IDs; no inference output or existing HF object was changed.

`web-examples.js`: each existing comparison has `has_source: true`; its other values are unchanged. The new `sections.teaser` array has six entries. `media-config.js` pins the revision above. All15 first-frame JPEGs are ordinary files under `static/posters/web/`, not symlinks.

**No layout edits:** `index.html`, `gallery.js`, `editorial.css`, `showcase-selection.js` are unchanged from3558358. Opus can now implement Source | Holo4D | Vista4D and a teaser mosaic. Neither new media group is wired into the current page layout by this commit.

## Exact video inventory

All are H.264/yuv420p, no audio, faststart,16FPS, CRF22. Size is exact bytes; dimensions are width×height. Paths below are relative to the HF prefix above.

| Task | New path | Width × Height | Frames | FPS | Duration (s) | Bytes |
|---|---|---:|---:|---:|---:|---:|
| A | `comparison/snow-dog/crane-above/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 272,733 |
| A | `comparison/fashion-walk/arc-left-right/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 522,867 |
| A | `comparison/mountain-hike/truck-crane-below/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 719,839 |
| A | `comparison/golf/dolly-out/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 1,080,628 |
| A | `comparison/drive-desert/side-fly/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 953,303 |
| A | `comparison/drive-desert/back-follow/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 953,303 |
| A | `comparison/woman-beach/crane-above/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 368,551 |
| A | `comparison/truck-pose/left-right/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 449,848 |
| A | `comparison/friends-restaurant/side-dolly/source.mp4` | 672 × 384 | 49 | 16 | 3.0625 | 242,302 |
| B | `teaser/01_figure-orbit/clean.mp4` | 384 × 672 | 96 | 16 | 6.0000 | 304,520 |
| B | `teaser/02_tesla-zoom/clean.mp4` | 384 × 672 | 96 | 16 | 6.0000 | 583,178 |
| B | `teaser/03_droid-gupta/clean.mp4` | 672 × 384 | 96 | 16 | 6.0000 | 257,179 |
| B | `teaser/04_droid-tri/clean.mp4` | 672 × 384 | 96 | 16 | 6.0000 | 694,884 |
| B | `teaser/05_davis-bear/clean.mp4` | 672 × 384 | 96 | 16 | 6.0000 | 724,440 |
| B | `teaser/06_davis-dance/clean.mp4` | 672 × 384 | 96 | 16 | 6.0000 | 645,411 |

TaskA posters are `comparison/<scene>/<trajectory>/source-poster.jpg`; TaskB posters are `teaser/<name>/poster.jpg`, on HF and mirrored below `static/posters/web/`. All are480px wide, JPEGq85, first frame without added text.

## Temporal and provenance checks

TaskA uses the actual sampler-emitted `source_rgb.mp4` beside each comparison's archived `pred_rgb.mp4`, rather than guessing a start time from a raw clip. Its frames0..48 correspond exactly to the existing comparison frame window;49frames at16FPS is3.0625seconds. No crop/letterbox was needed: all nine sampler inputs already have672×384. The existing Vista4D web outputs are also frame-index retimed to16FPS.

TaskB uses only raw generated `pred_rgb.mp4`, not source panels or overlays. It preserves the full native target canvas, including both384×672 portrait humanoids. Ping-pong is0..48,47..1 (96frames,6seconds), with no duplicated endpoints. Six clips total3,209,612bytes, each under1.5MB. Gupta uses `static_right_front` after keyframe review: the robot arm is more visible than in the originally considered `static_left_front`.

## Completed validation

- ffprobe: exact dimensions, frame count, frame rate, duration, H264/yuv420p and faststart for all15.
- Fully decoded frame-index correspondence against each original input, including every reverse-half teaser frame.
- Anonymous requests: all15 new MP4s return206 and video/mp4 for bytes0–1023; all15 JPEGs return200.
- `python tools/check_public_media.py --output <report>`:22 probes passed (legacy representatives plus all new MP4s).
- Chromium desktop1440/mobile390: initial page loads without JavaScript exceptions, lazy MP4 behavior retained; all15 new videos load and decode from the immutable hosted URLs, and all15 local posters return200.

Private validation root on Civo:
`/scratch/shared/engs2907/open-source/holo4d/opus_media_20261017_ab_v2/`.
Contains `media_manifest.json` (original paths and input/outputSHA256), `decoded_validation.json`, `hf_upload.json`, `public_media_check.json`, `browser_validation.json`, desktop/mobile screenshots and teaser contact sheet. These private provenance files are not uploaded as public media.

## Reusing the tools

Run CPU-heavy export/browser checks on a compute node. `tools/prepare_opus_media.py --output <fresh-root>` exports without overwriting; `tools/verify_opus_media.py --root <fresh-root>` verifies frames. The publisher refuses an already-existing HF destination; never rerun it with changed media at these same paths. Add a new path for any later revision. Existing `tools/package_page.py` and `tools/audit_storage.py` recognize source and teaser assets.

## Optional Task C status

RAD and TRI second-path candidates were inventoried, and Figure0 source/camera staging passed. No new Figure0 continuation was generated. The three singleton long results remain hidden until separately generated/reviewed and paired; do not label TaskC complete.
