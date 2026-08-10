# Holo4D project page

Project-page draft based on the Academic Project Page Template, with a simple
4RC-style layout and a 20-example video carousel.

## Local preview

Serve this directory with any static HTTP server, then open `index.html` through
the server. Direct `file://` loading is not recommended because browser video
policies differ.

## Draft asset provenance

The 20 source/condition/output triplets under `static/videos/50step/` are
absolute symbolic links to the corrected-camera 50-step B200 result root on
this machine; they do not duplicate MP4 data. Each `source.mp4` points to
`source_rgb.mp4`, and each `output.mp4` points to the generated trajectory MP4.
The temporary `condition-placeholder.mp4` points to matched `gt_rgb.mp4` only
for page-layout review. Holo4D does not receive target ground-truth RGB; replace
this placeholder with the actual hybrid RGB-D/validity, camera-ray, and 3D-track
condition visualization before publication.

These machine-local links work for local preview but are intentionally not a
deployable asset strategy. Replace them with hosted media URLs or publishable
assets before deploying the page anywhere that cannot access `/vgg/yushi/logs/`.

The paper button serves `static/pdfs/holo4d-paper.pdf`, an absolute symbolic
link to the current local submission PDF. Code, public paper/arXiv, canonical
URL, social preview, and final benchmark media should be updated before
publication.
