+++
title = "Component and typography showcase"
description = "Draft visual test page for the project authoring components."
template = "article.html"
draft = true

[extra]
kind = "explainer"
+++

## Ordinary typography

This paragraph exercises **strong emphasis**, *italics*, [an ordinary link](https://example.com/), `inline code` and a footnote.[^note]

1. First ordered item
2. Second ordered item with enough text to wrap naturally on a narrow screen and confirm that continuation lines remain aligned.
3. Third ordered item

- An ordinary bullet
- Another ordinary bullet

> A short block quotation for visual checking.

[^note]: Placeholder footnote content for visual checking.

## Callouts

{% <callout> %}
A note with **bold text**, an [example link](https://example.com/) and ordinary Markdown.

This second paragraph verifies multi-paragraph rendering.
{% </callout> %}

{% <callout kind="tip"> %}
A concise practical tip using its default title.
{% </callout> %}

{% <callout kind="warning" title="Custom warning title"> %}
A visible warning with a custom title.
{% </callout> %}

{% <callout kind="danger"> %}
A high-severity hazard using the default Danger title.
{% </callout> %}

{% <callout kind="local"> %}
A neutral local-practice note.
{% </callout> %}

{% <callout kind="not-a-kind"> %}
An unknown kind falls back safely to the note appearance and title.
{% </callout> %}

## Checklist

{% <checklist title="Static reference checklist"> %}
- First item with **emphasis**
- Second item with an [example link](https://example.com/) and enough text to wrap onto another line at narrow widths
- Third item
  - Nested item remains an ordinary subordinate list
{% </checklist> %}

{% <checklist> %}
- An untitled checklist confirms that the title is optional.
{% </checklist> %}

## Figure

{{ <figure page={page} src="equipment-placeholder.svg" alt="Abstract arrangement of labelled rectangular shapes" caption="A non-clinical page-bundle placeholder." credit="Project placeholder" /> }}

## Details

{% <details title="Optional supporting explanation"> %}
The disclosure body supports **Markdown** and [links](https://example.com/).

It also supports multiple paragraphs and an ordinary list:

- First supporting point
- Second supporting point
{% </details> %}

## Figure pair

{{ <figure_pair page={page} left_src="equipment-placeholder.svg" left_alt="First abstract arrangement of labelled rectangular shapes" left_caption="First non-clinical placeholder." right_src="equipment-placeholder.svg" right_alt="Second abstract arrangement of labelled rectangular shapes" right_caption="Second non-clinical placeholder." right_credit="Project placeholder" /> }}

## Table

| Column one | Column two | Column three | Column four |
| --- | --- | --- | --- |
| Short value | A deliberately longer value for narrow-screen overflow testing | Short value | Short value |
| Another value | Another value | Another value | Another value |
