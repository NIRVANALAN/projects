# Holo4D media storage and collaborator review

## Current Git/release audit — 2026-10-17

The Holo4D source folder occupies about **9MiB**, not hundreds of megabytes.
The main regular assets are the5,261,903-byte paper PDF and115 first-frame JPEG
covers (3,658,331bytes); the rest is HTML/CSS/JS, documentation and tooling.
Covers are deliberately versioned for fast same-origin previews. MP4s and
geometry/inference caches are **not committed**. Both local mount points
`static/videos/web` and `static/videos/postgen_20261012`, along with the old
`cowtracker/` cache, are ignored. Never add these absolute symlinks to Git.

The default page, **including a fresh localhost clone**, loads videos from the
already-public pinned HTTPS export and covers from `static/posters/web/`.
No Civo filesystem is needed for that mode. Only Civo cache review uses
`?local_media=1`, which enables the ignored local mounts and local-only
post-generation overlay replacements. This opt-in is refused on public hosts.

All406 required compact media files remain available (328,584,670bytes),
with no missing files in the full local inventory. Historical/unreferenced
exports remain in scratch and are excluded, not deleted. The offline portable
release is separate from the small Git checkout:

`/scratch/shared/engs2907/open-source/holo4d/project-page-release_20261017_editorial_v2/`

It contains532 regular files, no symlinks, and passed the desktop/mobile player
gate. It intentionally includes portable MP4 copies; GitHub uses external
MP4 hosting instead. Audit/screenshots:
`/scratch/shared/engs2907/open-source/holo4d/page_review_20261017/`.
The final clean-checkout-equivalent check and staged-file audit for publication
are recorded under `publication/` in that directory. Older release counts
below are dated historical snapshots, not the current Git size.

Publication gates passed: the full local desktop/mobile gallery test and a
Git-index-exported **mount-free checkout**. The latter served regular local
covers, decoded/played both actual HTTPS videos, and unloaded them offscreen.
Evidence: `publication/local_gate/home_style_validation.json` and
`publication/hosted_gate/clean_checkout_validation.json`. The exported Git-only
page is `publication/checkout_QtZrGZ/holo4d/` under the audit root. No MP4 or
symlink is present in the staged Holo4D tree. Only Holo4D changes are committed;
the unrelated `track4d/` worktree is excluded.

The website source is versioned in this repository. Original inference,
geometry caches, metrics and compressed web media live outside Git. The local
`static/videos/web` mount is intentionally ignored: committing an absolute
Civo symlink would not give collaborators working media.

## What is required

| Asset | Why retain it |
|---|---|
| `interleaved.mp4` | Default single-player clean/tracks presentation |
| `clean.mp4` | User's Clean mode; long videos; paired comparisons |
| `overlay.mp4` | User's Tracks mode; contains actual source-condition projection |
| `poster.jpg` | First-frame placeholder with lazy loading; avoids black cards |
| `baseline.mp4`, `baseline-poster.jpg` | Matched Vista4D comparison |
| `favicon.svg`, paper PDF | Header/favicon and paper link |

These three short MP4 variants are functional alternatives, not accidental
duplicates. Removing clean/overlay requires removing their mode controls; that
is not part of storage cleanup. PNG contact sheets and raw renders are review
artifacts, not public-page assets. Export signatures and provenance JSON stay
private for reproducibility and incremental rebuilding.

## Safe compact release

Audit on 2026-10-12: the working media cache contains **406 required public
files / 328,584,670 bytes**, 755 unreferenced exports / 573,838,405 bytes and
1,133 private JSON files / 1,780,593 bytes. No required files were missing.
The compact release contains 415 files (406 media plus nine page dependencies),
excluding about 574 MB of old exports without deleting them from the cache.
It is at:

```text
/scratch/shared/engs2907/open-source/holo4d/project-page-release_20261012_compact
```

Original caches remain at `project-page-media_20261009`. The private audit is
`/scratch/shared/engs2907/open-source/holo4d/project-page-review_20261012/storage_audit.json`.
This compact directory is a local review snapshot. Its required media has
since been uploaded as described below; the current website source is in Git.

`tools/package_page.py` follows `web-examples.js` and copies only the files the
current player references, plus actual HTML/CSS/JS/favicon/PDF dependencies.
It excludes prior export versions, large raw inference files, contact sheets,
private JSON and absolute symlinks. It preserves all listed current examples,
including evidence entries held out of the paired gallery.

From this directory on a compute node:

```bash
python tools/audit_storage.py --output /absolute/path/storage_audit.json
python tools/package_page.py --output /absolute/path/new-portable-review
```

The output path must not already exist. Do not point it at an original
inference root. Existing media remains recoverable; no pruning/deletion is
performed by these commands. Serve the portable directory as a static site
or use `tools/preview_page.py` there for byte-range support. Independent HTTPS
media hosting is supported by `static/js/media-config.js`; setting a base URL
does not upload media. No deployment is authorized by a local Git backup.

## Collaborator scope

Keep the current homepage-inspired neutral/blue style, robot-first layout,
same-source/two-camera pairing, aspect-ratio grouping, lazy posters, explicit
play/pause/seek and single-MP4 interleave. See `README.md` for the browser gate.
Suggest improvements without changing scientific results or claiming that
target-projected tracks are independently measured on generated RGB.

New CoWTracker + VGGT-Omega + GMOS reruns are requested for the current 4RC
examples. They are not yet substitutes for the existing media and must be
visually reviewed and accompanied by actual backend/camera provenance first.

## GitHub Pages repair and public media — 2026-10-12

Run 38232718545 failed while `upload-pages-artifact` dereferenced a tracked
absolute PDF symlink: `holo4d/static/pdfs/holo4d-paper.pdf: File removed before
we read it`. The link is replaced by the same actual 5,261,903-byte PDF;
the research original remains untouched. Do not commit absolute Civo symlinks.

All 406 current compact public media uploaded to the existing
`yslan/Holo4D-2026` model repository, folder `project_page/media_20261012`,
commit `d961d338edf61d0f3e2786e4ced60be69c02bcda`. Only MP4/JPG uploaded;
no private JSON or historical cache. The public page pins this exact HTTPS
revision; localhost previews still use relative files. Lazy loading and
clean/tracks/interleave controls remain unchanged. Upload entrypoint:
`tools/upload_public_media.sh` (compute-node CPU2/noGPU).

[Pages run 38235155355](https://github.com/NIRVANALAN/projects/actions/runs/38235155355)
built and deployed commit `b489f58` successfully. The live site is
[Holo4D](https://nirvanalan.github.io/projects/holo4d/).
The current desktop/mobile browser gate passed against this actual live URL:
all nine long videos decoded, byte-range HTTP 206 worked, poster-first loading
made no eager MP4 requests, and playback, seeking, paired buffering and
clean/tracks/interleave controls passed. Evidence:
`/scratch/shared/engs2907/open-source/holo4d/project-page-review_20261012/browser_live_pages/home_style_validation.json`.
