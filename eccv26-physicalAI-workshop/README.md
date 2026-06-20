# PhysAI 2026 — Workshop Website

Static site for the 1st Workshop on **Physical AI: Understanding and Building the Physical World**, held in conjunction with **ECCV 2026**.

## Local preview

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

The site is plain HTML/CSS/JS — no build step required. It can be deployed to GitHub Pages, Netlify, or any static host by serving the repo root.

## File layout

```
index.html        # Page markup and copy
styles.css        # All styles (no framework)
data.js           # Speaker & organizer lists (edit to update people)
script.js         # Renders speaker/organizer cards from data.js
assets/
  organizers/    # Organizer profile photos
  speakers/      # Invited-speaker profile photos
```

## Updating people

Edit `data.js` to add/remove speakers or organizers. The `photo` field is a relative path under `assets/`; if the file is missing or fails to load the renderer falls back to a colored placeholder with the person's initials.

## Inspiration

- Layout & structure: <https://forecasting-workshop.github.io/>
- Challenge section: <https://mipi-challenge.org/MIPI2025/>
