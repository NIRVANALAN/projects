# Holo4D media storage and collaborator review

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
This is local staging, not an upload or remote deployment.

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
