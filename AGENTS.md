# Project-page visual identity

For new pages and requested restyling, follow [DESIGN_LANGUAGE.md](DESIGN_LANGUAGE.md).
The user's personal homepage (https://nirvanalan.github.io/) is the palette and
typography authority: Lato, white/neutral-gray surfaces, dark text, blue links,
orange link hover. Do not introduce green/teal themes. The reusable stylesheet
is `template/static/project.css`; keep each project's own content/layout.

Preserve poster-first lazy media loading, explicit Play/Pause and seeking.
Group portrait and landscape examples, with two cards on desktop and one on
mobile. Keep original inference and evaluation media immutable; presentation
filters/compression belong in separate export roots. Do not change another
project's page without it being in the current request's scope.

Run CPU-heavy media exports and browser checks on compute nodes, not Civo's
login node. Do not publish or change the website's remote audience merely for
a local visual update. Check actual screenshots as well as browser assertions.
