# Authoring Praxis

The site is tested with Zola 0.22.1. Its reusable authoring elements are Zola **shortcodes**, using `{% name(...) %}…{% end %}` for elements with a body and `{{ name(...) }}` for elements without one. Do not mix in the Tera component syntax introduced in Zola 0.23.

## Add a procedure family

Create a directory below `content/procedures/` and add `_index.md`:

```toml
+++
title = "Family name"
# description = "Optional, genuinely useful scope statement."
template = "family.html"
page_template = "article.html"
sort_by = "title"
# weight = 10
+++
```

The homepage and procedure directory discover the family automatically. Use `weight` to control its position relative to other procedure areas. Omit the description and Markdown body unless they add useful scope or context beyond the title; do not add boilerplate introductory text.

## Add a guide or explainer

Copy `examples/guide.md` or `examples/explainer.md` into a page-bundle directory beneath the family and name it `index.md`:

```text
content/procedures/family-slug/article-slug/
  index.md
  article-image.svg
```

Set `draft = true` until the clinical and editorial review is complete. The family page discovers published pages automatically and groups guides before explainers.

Suggested guide headings are Overview and scope, Indications and considerations, Equipment, Preparation, Technique, Immediate checks, Aftercare, Troubleshooting and References. Keep the practical sequence together on one page. Explainers should begin with a short answer and then cover reasoning, trade-offs and evidence.

## Front matter

Use Zola’s native fields wherever they fit:

```toml
+++
title = "Clear article title"
description = "A concise summary."
authors = ["Named author"]
template = "article.html"
draft = true
# date = YYYY-MM-DD
# updated = YYYY-MM-DD

[extra]
kind = "guide"
# reviewed = "YYYY-MM-DD"
# related = ["procedures/family-slug/another-page/index.md"]
+++
```

`extra.kind` supports `guide` and `explainer`. If omitted, templates treat the page as a guide.

The optional dates have distinct meanings:

- `date` is the original publication date.
- `updated` is the date of the latest substantive published revision, when different from `date`.
- `extra.reviewed` is the date of an actual clinical content review.

Use native, unquoted TOML dates for `date` and `updated`. Keep `reviewed` as a quoted `YYYY-MM-DD` value in `[extra]`. Never infer any of these from a file modification or build date. Omit unknown dates, authors and reviewers rather than inventing them.

`related` contains content-root-relative **source paths**, including the `.md` filename. Templates resolve the target with Zola, display its real title and URL, and fail the build if a path is invalid. A public page must not relate to a draft page because that target is absent from a public build.

## Internal links and references

Use Zola internal links so moves and broken targets are validated:

```markdown
Read [the site-selection explainer](@/procedures/central-venous-access/choosing-a-site/index.md).
```

Use descriptive link text. Keep reference lists as ordinary Markdown numbered lists. Link to primary guidance or evidence where possible and follow the project’s chosen reference style consistently.

## Images

Put article images beside `index.md` in the page bundle. Normal Markdown images remain available:

```markdown
![Useful alternative text](image-name.svg)
```

Use the figure shortcode when a caption or credit is needed. `src` and `alt` are required; `caption` and `credit` are optional:

```markdown
{{ figure(src="image-name.svg", alt="Describe the information in the image", caption="Optional caption.", credit="Optional source") }}
```

The figure shortcode validates the page-relative asset through Zola and emits its intrinsic dimensions. Its relative URL remains correct on nested routes and when the site is hosted below a URL prefix. Captions and credits are plain text and are escaped automatically. Do not put Markdown in those parameters.

### Figure pair

Use `figure_pair` for exactly two related figures. Each image has required `src` and `alt` parameters and optional `caption` and `credit` parameters, prefixed with `left_` or `right_`. The two semantic figures share one visual container, appearing side by side when space permits and stacking within the same card on narrow screens.

```markdown
{{ figure_pair(
  left_src="first-image.svg",
  left_alt="Describe the first image",
  left_caption="Optional first caption.",
  right_src="second-image.svg",
  right_alt="Describe the second image",
  right_caption="Optional second caption.",
  right_credit="Optional source"
) }}
```

Keep both images in the article’s page bundle. Use two ordinary figure shortcodes instead when the images are not meaningfully related.

## Callout

Parameters: optional `kind` (default `note`) and optional `title`. Supported kinds are `note`, `tip`, `warning`, `danger` and `local`. Unknown values fall back safely to `note`.

Default titles are Note, Practical tip, Warning, Danger and Local practice respectively. Reserve `danger` for the most serious hazards; use `warning` for ordinary cautions.

```markdown
{% callout(kind="warning", title="Before proceeding") %}
Important reviewed text goes here. Links and **emphasis** work normally.
{% end %}
```

```markdown
{% callout(kind="danger") %}
State the serious hazard and the action needed to avoid it.
{% end %}
```

Callouts are static, visible content—not screen-reader alerts. Do not hide core precautions in a details disclosure.

## Checklist

The optional `title` parameter labels the panel. Write one ordinary Markdown bullet list in the body; do not invoke the shortcode once per item.

```markdown
{% checklist(title="Equipment") %}
- Procedure-specific equipment
- Monitoring equipment with **important detail**
- Supporting documentation
  - Nested items remain normal subordinate bullets
{% end %}
```

The square markers are decorative. The list remains semantic and is not interactive completion tracking.

## Details

The `title` parameter is required. The body supports ordinary Markdown and uses native `details`/`summary` without JavaScript.

```markdown
{% details(title="Why this approach?") %}
Optional background explanation can include **emphasis**, links and lists.

- First supporting point
- Second supporting point
{% end %}
```

Use details only for optional background or evidence. Disclosed content is forced open in print.

## Draft and review workflow

Preview drafts with `zola serve --drafts`. Run both public and draft checks before publishing:

```sh
zola check --skip-external-links
zola check --drafts --skip-external-links
```

Before changing `draft` to `false`, replace every labelled placeholder, confirm references and local-policy links, obtain the required review, and add `extra.reviewed` only if that review actually happened.
