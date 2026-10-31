+++
title = "Procedure title"
description = "Preparation, technique and aftercare."
template = "article.html"
draft = true
# date = YYYY-MM-DD
# updated = YYYY-MM-DD

[extra]
kind = "guide"
# reviewed = "YYYY-MM-DD"
# reviewers = ["Named clinical reviewer"]
# related = ["procedures/family-slug/explainer-slug/index.md"]
+++

## Overview and scope

State what the guide covers, who it is for and important limits.

## Indications and considerations

Add reviewed indications, contraindications, alternatives and patient-specific considerations.[^primary-source]

## Equipment

{% <checklist title="Equipment"> %}
- Procedure-specific equipment
- Monitoring equipment
- Supporting documentation
{% </checklist> %}

## Preparation

Describe preparation in ordinary Markdown.

{% <callout kind="warning" title="Before proceeding"> %}
Add the most important reviewed precaution here.
{% </callout> %}

## Technique

{% <step number={1} title="Perform the main stage"> %}
Introduce this stage of the procedure and explain what its illustration shows.

{{ <figure page={page} src="guide-figure.svg" alt="Three labelled abstract shapes connected in sequence." caption="Non-clinical placeholder: replace with a reviewed procedure illustration and caption." /> }}

1. First reviewed action within this stage.
2. Second reviewed action.
3. Confirm the expected result before continuing.[^primary-source]

{% <callout kind="tip" title="Practical detail"> %}
Add a concise practical detail.
{% </callout> %}
{% </step> %}

{% <step number={2} title="Complete the procedure"> %}
Describe the next stage, including the checks needed before finishing.
{% </step> %}

{% <details title="Why this approach?"> %}
Add optional supporting reasoning and evidence.
{% </details> %}

## Immediate checks

Add immediate checks and escalation criteria.

## Aftercare

Add documentation, observation and follow-up requirements.

## Troubleshooting

| Situation | Response |
| --- | --- |
| Example | Add a reviewed response. |

## References

[^primary-source]: Add current primary guidance and evidence, with a linked source title.
