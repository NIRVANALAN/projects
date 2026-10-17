# Project-page template

Buildless starting point for new project pages in the style of
[nirvanalan.github.io](https://nirvanalan.github.io/): Lato 15.5px, 1040px column,
24px section titles over a soft rule, blue links with orange hover, `/`-separated
link row, 4px-rounded media, small right-aligned footer.

```bash
cp -R template my-project   # then edit my-project/index.html
```

- `static/project.css` — the only stylesheet; tokens on `:root`.
- `static/project.js` — videos load and play only on screen; Copy for BibTeX.
- Videos: `<video data-src="…mp4" poster="…jpg">` inside `.media`; set `--aspect`
  on `.media` for non-16:9 clips. H.264, yuv420p, `+faststart`.
- Layout blocks: `.grid-2` (paired results), `.grid-3`, `.compare` (ours | baseline),
  `.wide` (teaser), `.prose` (reading width).

Content rules are in [DESIGN_LANGUAGE.md](../DESIGN_LANGUAGE.md).
