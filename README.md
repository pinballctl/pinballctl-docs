# pinballctl-docs

Documentation repository for the `pinballctl` project.

## Project Repositories

- `pinballctl` = `app`
- `pinballctl-website` = `website`
- `pinballctl-docs` = `docs`

When referring to repos in tasks, the aliases above are the canonical shorthand.

## Source Structure

- Markdown source pages: `pages/`
- Docs assets (screenshots/diagrams): `assets/`
- Build utilities: `utils/`
- Generated static site output: `index.html`, `site-data.json`

`pages/` is the renamed/manual-free source folder for docs content.

## Build (On Demand)

Run this to regenerate the static docs site from markdown:

```bash
./utils/build-docs-site.py
```

What it does:

- parses markdown files in `pages/`
- renders HTML content
- rewrites legacy `/api/manual/assets/...` links to local `./assets/...`
- builds navigation tree + search data in `site-data.json`
- generates `index.html`

## Layout/Design

The docs site uses the same visual base as `website` by syncing `style.css` from `pinballctl-website` during build (when that repo exists beside this one).

Docs-specific layout rules live in `docs.css`.

## Features

- Client-side docs tree navigation
- Client-side search (no backend needed)
- Local bookmarks (stored in browser `localStorage`)
- Click-to-zoom screenshots

## Screenshot Automation Metadata (Draft)

Markdown files can declare screenshot instructions using an inline JSON directive comment:

```md
<!-- pinballctl-shot {"url":"http://raspberrypi.local:8888/login","click":["text=Sign in"],"wait_for":"#dashboard","output":"assets/screenshots/dashboard.png"} -->
```

Validate/inspect directives:

```bash
./utils/capture-doc-screenshots.py
```

This parser script currently lists and validates directives; browser automation capture can be wired next.
