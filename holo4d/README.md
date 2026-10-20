# Holo4D project page

## Media-first editorial revision — 2026-10-17

Current local revision moves the existing robot gallery directly below the
paper masthead, puts gallery controls below videos, and folds repeated
provenance into `Sample details`. All curated source/camera pairings and nine
approved long videos are retained. White/Lato/blue homepage identity is
unchanged; no duplicate hero. `static/css/project.css` is the single page stylesheet.

Public first-frame covers are regular same-origin files under
`static/posters/web/` (115 JPEGs, about3.66MB total); MP4s remain pinned HTTPS,
viewport-only. `tools/prepare_page_posters.py` refreshes these derived covers
atomically. Thumbnail loading now follows the browser viewport, not just the
horizontal thumbnail strip. Source-tree media symlinks remain development
mounts; `tools/package_page.py` produces a symlink-free portable release.

Desktop/mobile/player evidence:
`/scratch/shared/engs2907/open-source/holo4d/page_review_20261017/`.
Portable local copy:
`/scratch/shared/engs2907/open-source/holo4d/project-page-release_20261017_editorial_v2/`.
Detailed handoff:
`/vgg/yushi/Repo/track4d-360/doc/new_features/2026-10-17-media-first-project-page-polish.md`.
This revision is prepared for remote publication; deployment success is
separate from a successful Git push. See [STORAGE.md](STORAGE.md) for the
small Git checkout versus the optional full offline media package.

A fresh clone uses hosted MP4s and regular same-origin posters, even when
served on localhost. Civo-only cache/post-generation preview requires
`?local_media=1`; the ignored scratch mounts are never required by the public page.


## Curated existing samples — 2026-10-12

`static/js/showcase-selection.js` selects14robot shorts and12mixed
DAVIS/native shorts from the unchanged media catalogue. Each short pair has
the same exact source and two distinct camera paths. All nine author-approved
robot long videos remain; the nine Vista4D comparisons now start with golf,
drive-desert and friends-restaurant. Current DROID4RC and humanoid/nativeCoW
backends are retained. Inconclusive new resolution gates are not substituted.
Classic-car, breakdance and slow-dolly foreground diagnostics are not in this
default shortlist; archive files remain intact. No new media upload is needed.
Details and validation:
`/vgg/yushi/Repo/track4d-360/doc/new_features/2026-10-12-curated-existing-project-page-showcase.md`.

## Homepage style — current revision, 2026-10-11

Latest gallery correction: robots precede Video reshooting. Short desktop rows
pair two distinct trajectories from the **same exact source ID**; Figure and
Tesla headings omit clip numbers without merging different recordings. DAVIS
and native Vista4D examples share one gallery. Visible players buffer together
before startup, preserving independent Play/Pause/seek and on-demand loading.
Singletons remain archived, not paired with unrelated scenes. Historical
classic-car CoW/GMOS exports are review-only until the preferred good sample is
identified; the rejected 4RC example is not displayed. Details and CPU launcher:
`/vgg/yushi/Repo/track4d-360/doc/new_features/2026-10-11-same-scene-paired-project-gallery.md`.

The visual authority is [Yushi's homepage](https://nirvanalan.github.io/), not
the earlier green/teal experimental theme. Reusable identity tokens live in
`../template/static/project.css`: Lato with local sans-serif fallback, white,
`#222` text, `#1772d0` links and `#f09228` hover. Buttons/cards are neutral gray.
Google Fonts is optional; no media or player depends on its availability.
Copy this theme to subsequent project pages; retain each project's own layout.

The redundant hero video is removed. Portrait humanoids and landscape arms
have separate two-card galleries; all nine approved long rollouts are grouped
the same way. Each video has an explicit Play/Pause button and seeking. The
last odd carousel page overlaps its neighbor instead of showing an empty slot.
Single-MP4 clean/tracks interleave remains unchanged.

Current gate: `tools/test_home_style_showcase.py`. The102-entry export and
complete desktop/mobile gate passed, including four AB12 step-19500 DAVIS
examples. Nine long web videos have no yellow boundary box. Breakdance and
DAVIS use filter v2; the remaining strict-filter batch is still running.
Previous complete overlays are retained until replacements finish.
Research launcher:
`/vgg/yushi/Repo/track4d-360/bash_scripts/track4d_360/civo/rebuttal/run_home_style_page_refresh_cpu.sh`.
The older editorial descriptions below document the superseded revision.

## Storage and collaborator handoff — 2026-10-12

[STORAGE.md](STORAGE.md) explains which MP4/poster variants the player uses,
which caches are excluded from deployment, and how to stage a compact review.
The audited portable copy has415files including328.6MB of active media;573.8MB
of old unreferenced exports are excluded, not deleted. Local media mounts and
Python caches are ignored by Git. This backup contains website source only;
media hosting/deployment is documented separately in the storage guide.
The live page now uses pinned HTTPS media on Hugging Face, and the paper PDF
is a portable real file. Pages deployment and the live desktop/mobile browser
gate passed on 2026-10-12. To repeat the current gate in the browser-test environment:

```bash
python tools/test_home_style_showcase.py --url https://nirvanalan.github.io/projects/holo4d/ --output /absolute/path/browser-review
```

## Editorial refresh — 2026-10-11

Retains the current Holo4D layout and all approved media. Design references:
[Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template),
[VideoMimic](https://www.videomimic.net/) and
[PersistBench](https://www.guangzhaohe.com/persistbench/).
The refresh adds a compact NeurIPS masthead, restrained section typography,
wide-screen-only contents sidebar, tablet/mobile section navigation, collapsible
protocol notes, per-gallery scene selection, synchronized comparison scrubbing,
keyboard focus styles and a back-to-top link. No remote fonts or framework
dependencies were added. `static/css/project.css` contains the consolidated page styles.

The browser gate validates all nine robot long videos, scene jumps, paired
seeking, byte-range 206, mobile explicit-load behavior and tablet overflow.
Screenshots/report:
`/scratch/shared/engs2907/open-source/holo4d/project-page-review_20261011/browser_template_polish/`.
Changes are local, not published. Media and inference results are unchanged.
Portable static copy with382referenced assets and resolved media symlinks:
`/scratch/shared/engs2907/open-source/holo4d/project-page-release_20261011_editorial/`.
The same browser gate passed against the portable copy; report is in
`browser_template_polish_portable/` alongside the source-tree screenshots.

Academic layout with a robot-first teaser and separate scene/robot/long-video/
Vista4D-comparison galleries. The earlier historical gallery is removed. Two examples
per desktop view,one on mobile. MP4 URLs are assigned only when a gallery is on
screen; unloaded cards show first-frame posters,not black.

## Current web pipeline (2026-10-11)

- `tools/curate_web_media.py`: freezes53 filtered robot examples,27 native examples,
  9 paired Vista4D comparisons and all9 author-approved robot long rollouts.
  Rejected originals stay on disk but are excluded from the page.
  `build_web_media.sh` defaults to this selection, not the historical manifest.
- `tools/export_web_media.py`: incremental CPU H.264/yuv420p/CRF22/max-width960/
  faststart export,first-frame JPEGs,frame/pair checks and private provenance.
  Original FPS is preserved except comparison baseline copies:49frames retimed
  from25FPS to match Holo4D16FPS. Raw predictions/metrics are not changed.
- `static/js/gallery.js`: viewport-only loading,offscreen unload/pause,
  one player per short example using a clean/tracks interleaved MP4. Clean/Tracks
  modes load their independent copies only on request.
  Mobile and reduced-motion behavior are included. Save-Data/2G and reduced
  motion request no MP4 until explicit play. The global data-saver selector
  requires consent per carousel page; no neighboring videos are prefetched.
  Loading status, error recovery with Retry, and aspect-safe Expand
  are available without changing the clean/tracking display.
- `static/js/media-config.js`: pinned HTTPS video and same-origin poster roots by default.
  Change these to approved HTTPS directories only after the media is published;
  configuring a URL does not upload or deploy anything. External HTTP is refused
  except a loopback-to-loopback development preview. Credentials/query tokens
  and fragments are refused. Serve byte ranges and `video/mp4` from the host.
- Portrait previews rearrange three complete portrait panels horizontally;
  no subject crop or inference change. Landscape keeps the established layout.
- `tools/package_page.py`: portable local staging with resolved symlinks and
  referenced public assets only; excludes raw-path metadata. No deployment.

Run on a compute node from this directory:

```bash
bash tools/build_web_media.sh
```

Web media:
`/scratch/shared/engs2907/open-source/holo4d/project-page-media_20261009/`,
linked locally as `static/videos/web` (explicit `?local_media=1` preview). The active manifest is
`static/js/web-examples.js`; original V4/selected inference files are intact.
`curation.json`,`export_validation.json` and per-case `provenance.json` record
selection/compression. Private metadata is not copied into releases.

Stage a fresh portable release after checking publication rights:

```bash
python tools/package_page.py --output /absolute/path/to/new/static-release
```

Current browser regression: `tools/test_revised_showcase.py` (isolated Playwright environment,
not installed into the model environment). Older two-player tests document the
superseded layout. The current gate loads all9 long videos and checks byte-range206.
Long videos have source/generated panels only; no continuous track export is claimed.
All9 author-approved long previews are0.43–1.17MB each (decimalMB), H.264/faststart,
with full81–246frames at16FPS. This is local publication-ready staging, not deployment.
Paper stills and provenance are in
`/scratch/shared/engs2907/open-source/holo4d/paper-assets_robot-long-approved9_20261011/`;
handoff: `/vgg/yushi/Repo/track4d-360/doc/new_features/2026-10-11-approved-robot-long-rollout-paper-pack.md`.
Comparison cards distinguish
per-video metric wins from author-selected qualitative examples.

## Local preview

Serve this directory with any static HTTP server, then open `index.html` through
the server. Direct `file://` loading is not recommended because browser video
policies differ.

Recommended local preview (byte ranges,ETag and media cache headers):

```bash
python tools/preview_page.py --port 8080
```

Bind is localhost only; SSH-forward8080 from your laptop. To inspect portable
staging,add `--directory /scratch/shared/engs2907/open-source/holo4d/project-page-release_20261009_v3`.
Use a real static host/CDN for publication,not this preview service.

## Legacy draft asset provenance (not the active manifest)

The archived page version used62 complete pairs under
`static/videos/cowtracker/`: 39 from `ab12_step19500` and 23 from
`dense_id_target_step22000`. Every `clean.mp4` points to
`13_source_condition_synth_clean.mp4`; every `overlay.mp4` points to the
frame-aligned `11_vista4d_style_source_condition_synth.mp4`; every `thumb.jpg`
points to the existing condition-explainer cover used by the thumbnail
navigator. The page stacks each pair and cross-fades once per source-video
loop. These are absolute soft
links to `/scratch/shared/engs2907/logs/track4d-360/project_page/v4/cowtracker/`
`vista4d_cherrypick`; no media is copied into this repository.
The old teaser used `friends-restaurant/crane-below`; the current hero uses
Figure1 / subject_orbit_zoom from the filtered selection. Historical compressed
archive copies remain on disk but are not referenced by the current HTML.

Regenerate legacy links and `static/js/examples.js` (not active
`web-examples.js`) with:

```bash
python3 tools/link_cowtracker_assets.py --verify-pairs
```

These machine-local links work for local preview but are intentionally not a
deployable asset strategy. Replace them with hosted media URLs or publishable
assets before deploying the page anywhere that cannot access
`/scratch/shared/engs2907/logs/`.

The paper button, `citation_pdf_url` and the BibTeX point to arXiv
(2610.25276); the Code button points to https://github.com/NIRVANALAN/Holo4D.
Canonical URL, social preview, and final benchmark media should be updated before
publication.

## TODO

Template lineage: [4RC](https://yihangluo.com/projects/4RC/) (base layout) →
this page; also scavenging UI ideas from
[Zero-WAM](https://robbyant-research.github.io/Zero-WAM/) (Academic Project
Page Template family).

Delivery/organization reference audit: [Vista4D](https://eyeline-labs.github.io/Vista4D/)
and its [actual carousel runtime](https://eyeline-labs.github.io/Vista4D/static/js/index.js),
plus the sibling Track4D project's media-policy implementation. Holo4D keeps
its own scientific descriptions, labels, assets and citation. Unlike Vista4D's
neighbor prefetch, this page does not speculatively fetch adjacent MP4s.

### Content / publication blockers
- [x] Implement portable staging with `tools/package_page.py`; only referenced
      media is copied and all symlinks are resolved. External publication and
      media-rights review still need approval.
- [x] Swap in the public paper/arXiv link (2610.25276): paper button,
      `citation_pdf_url` and BibTeX. `og:url` still to set.
- [x] Turn on the Code link (public repo NIRVANALAN/Holo4D).
- [x] Organize selected current examples,comparison metrics and the historical
      archive separately; exclude known content failures. Final public selection
      can still be narrowed after review.
- [ ] Add a social preview image (`og:image` / `twitter:image` are missing).
- [ ] Keep "Concurrent Works" current as new video-reshooting / video-to-4D
      papers appear (e.g. Vista4D, Lyra-[1,2]); re-check before submission.

### UI ideas borrowed from Zero-WAM (worth adapting)
- [x] Add a per-example caption/description line under each carousel slide
      (task or camera-trajectory description), not just the video label.
- [x] Split examples into scene,robot,long,comparison and archive galleries.
- [x] Add scroll-spy active-link
  highlighting on the contents sidebar — Zero-WAM's `setupTableOfContents`
  pattern is a useful reference.

## Local post-generation robot tracking preview (2026-10-12)

The 14 selected robot shorts and nine full rollouts retain their original RGB.
After validation, `static/js/postgen-preview.js` enables new CoW tracking only
for localhost previews. The generated-video overlay is **post-generation
tracking**, not the geometry condition fed to Holo4D. Original conditioning and
metrics remain unchanged. Public HF media is not silently replaced; portable
packaging uses an empty preview override until a separate media release.
Export root: `/scratch/shared/engs2907/logs/track4d-360/project_page/postgen_robot_showcase_all_20261012/`.
