# Yushi's project-page visual language

Style authority: [personal homepage](https://nirvanalan.github.io/), specifically
its `stylesheet.css`, inspected2026-10-11. Preserve consistency across projects
without forcing identical content layouts.

| Token | Default |
| --- | --- |
| Typeface | Lato400/700; Verdana/Helvetica/sans-serif fallback |
| Background / body text | `#fff` / `#222` |
| Muted text / subtle rules | `#666` / `#e5e5e5` |
| Links | `#1772d0` |
| Link hover | `#f09228` |
| Buttons / selected controls | Charcoal and neutral grays |

New pages: start from [`template/`](template/README.md) (`cp -R template my-project`).
Older pages: `holo4d/static/css/yushi-theme.css` remains the drop-in theme layer;
load it after project-specific layout CSS.
It is intentionally small and buildless. Lato's remote font is optional; the
fallback must remain readable offline. Do not introduce green/teal branded
badges, tinted cards or broad colored backgrounds. Keep research track identity
colors distinct from interface colors; do not recolor scientific overlays.

## Content and media conventions

- Paper title black; authors blue; venue (e.g. NeurIPS2026) below affiliations.
- Neutral, compact Paper/Code links. No duplicate hero if it repeats a gallery.
- Group portrait and landscape examples; two visible examples on desktop,
  one on mobile. Avoid an empty final carousel slot.
- For paired camera-reshooting showcases, each desktop row must use the
  same exact source clip with two distinct trajectories. Pair by persistent
  source ID, not a display name or arbitrary adjacent card. Odd groups may
  overlap only within that source; singletons remain archived until paired.
- Gate playback on readiness of all currently visible players; a late right
  response must not let the left video start early. Preserve individual seeking.
- First-frame posters, viewport-scoped downloads, offscreen pause/unload,
  explicit Play/Pause and timeline. Data saver/reduced motion require a click.
- Prefer one-video clean/tracks interleave over two independent moving players.
- H.264/yuv420p, faststart, byte-range hosting; preserve inference originals.
- Simple labels for chunks, not flashing yellow separators.
- Do not fabricate comparison assets, performance claims or results to fill a
  visual gap. Reuse a same-source neighbor or clearly identify missing assets.

Interaction/layout references: Academic Project Page Template, VideoMimic,
PersistBench. They do not replace the homepage palette. New pages should pass
desktop/mobile browser checks and inspect screenshots, not only source tests.
