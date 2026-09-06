# Praxis

A small Zola site for practical procedure guides and supporting explanations aimed at UK clinicians. Content is organised by procedure family and written primarily in Markdown.

## Requirements

This project was built and tested with **Zola 0.22.1**. That version uses Zola shortcodes; Zola 0.23 and later replace them with Tera components and are not source-compatible with this authoring API.

Install Zola using the [official installation instructions](https://www.getzola.org/documentation/getting-started/installation/) and confirm the version:

```sh
zola --version
```

For Cloudflare Pages, set `ZOLA_VERSION` to `0.22.1` in both production and preview build environment variables, with build command `zola build` and output directory `public`. This keeps builds on the supported version when Cloudflare changes its default. Use the same Zola version for local checks.

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

Zola writes generated files to `public/`. Do not edit that directory.

## Configuration

Site-wide settings live in `zola.toml`. Change `title` to update the header wordmark, browser titles and footer in one place. Set `base_url` to the canonical deployment URL; templates use Zola URL helpers so they also work below a URL prefix.

No Node tooling, CSS framework, JavaScript application, CMS or external font service is required. The site uses Tera templates, one plain CSS file and system fonts.

## File layout

```text
content/                 Published content tree and page-bundle assets
  procedures/            Procedure families, guides and explainers
  showcase/              Draft component and typography test page
templates/               Page shells, shared partials and TOC macro
  shortcodes/            Zola 0.22 authoring components
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
