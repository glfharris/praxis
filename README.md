# Praxis

A small Zola site for practical procedure guides and supporting explanations aimed at UK clinicians. Content is organised by procedure family and written primarily in Markdown.

## Requirements

This project uses **Zola 0.23.4** and Tera 2 components. Zola 0.22 and its shortcode syntax are no longer supported.

Install Zola using the [official installation instructions](https://www.getzola.org/documentation/getting-started/installation/) and confirm the version:

```sh
zola --version
```

For Cloudflare Pages, set `ZOLA_VERSION` to `0.23.4` in both production and preview build environment variables, with build command `zola build` and output directory `public`. This keeps builds on the supported version when Cloudflare changes its default. Use the same Zola version for local checks.

## Preview, build and check

Preview published content:

```sh
zola serve
```

Preview the unfinished demonstration guide, explainer and component showcase:

```sh
zola serve --drafts
```

Build the public site:

```sh
zola build
```

Build a draft preview:

```sh
zola build --drafts
```

Check templates and local links without relying on network access:

```sh
zola check --skip-external-links
zola check --drafts --skip-external-links
```

Run the build-level regression checks with Python 3 (standard library only):

```sh
python3 tests/check_site.py
```

These build temporary copies of the site and check draft exclusion, component escaping and Markdown, nested contents links, default guide classification, and missing-image validation.

To check the optional contents-highlighting script, run `node --test tests/article-navigation.test.mjs` with Node.js. Node is only needed for this development check, not for building or serving the site.

Zola writes generated files to `public/`. Do not edit that directory.

## Configuration

Site-wide settings live in `zola.toml`. Change `title` to update the header wordmark, browser titles and footer in one place. Set `base_url` to the canonical deployment URL; templates use Zola URL helpers so they also work below a URL prefix.

No Node tooling, CSS framework, JavaScript application, CMS or external font service is required to build the site. It uses Tera templates, one plain CSS file and system fonts. A small optional script highlights the current article section in the contents list; navigation and content remain usable without JavaScript.

The header mark and SVG favicon share `static/favicon.svg`. PNG and ICO fallbacks are committed, so normal site builds need no image tooling. After editing the SVG, regenerate them with librsvg and ImageMagick:

```sh
rsvg-convert -w 32 -h 32 static/favicon.svg -o static/favicon-32.png
rsvg-convert -w 180 -h 180 static/favicon.svg -o static/apple-touch-icon.png
magick static/favicon-32.png -define icon:auto-resize=32,16 static/favicon.ico
```

## File layout

```text
content/                 Published content tree and page-bundle assets
  procedures/            Procedure families, guides and explainers
  showcase/              Draft component and typography test page
templates/               Page shells and shared partials
  components/            Tera 2 authoring components and recursive TOC
static/site.css          Design tokens and responsive/print styles
docs/AUTHORING.md        Authoring contract and copyable recipes
examples/                Starter guide and explainer outside the site
```

Routine decisions made for this bootstrap:

- Procedure-family and article lists come from the content tree; there is no menu registry.
- A missing `extra.kind` is treated as `guide`.
- Unknown callout kinds fall back to `note`.
- Related-page source paths are resolved strictly at build time, so an invalid path fails validation.
- Draft clinical demonstrations contain labelled placeholders rather than unreviewed instructions.

See [docs/AUTHORING.md](docs/AUTHORING.md) before adding content.
