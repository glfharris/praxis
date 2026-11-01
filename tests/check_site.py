"""Build-level migration checks. Run with: python3 tests/check_site.py"""

from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]


class Markup(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.tags = []
        self.text = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, text):
        self.text.append(text)

    def attrs(self, tag):
        return [attrs for name, attrs in self.tags if name == tag]


class SiteMigrationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="praxis-migration-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.site = Path(cls.temp.name)
        for directory in ("content", "templates", "static"):
            shutil.copytree(ROOT / directory, cls.site / directory)
        shutil.copy2(ROOT / "zola.toml", cls.site / "zola.toml")
        fixture = cls.site / "content/procedures/central-venous-access/migration-check"
        fixture.mkdir()
        shutil.copy2(ROOT / "content/showcase/equipment-placeholder.svg", fixture)
        cls.fixture = fixture / "index.md"
        cls.fixture.write_text('''+++
title = "Migration check"
draft = true
[extra]
reviewers = ["Reviewer & colleague"]
+++

## Parent heading

### Child heading

A repeated source.[^primary]

{% <callout kind="unknown" title='A "quote" & <em>literal</em>'> %}
First **strong** paragraph with a [link](https://example.com/).[^primary]

Second paragraph.
{% </callout> %}

{% <checklist> %}
- Outer item
  - Nested item[^primary]
{% </checklist> %}

{% <details title='A "quote" & <em>literal</em>'> %}
Optional **detail**.[^primary]
{% </details> %}

{% <step number={1} title="A step with sources"> %}
A source inside a step.[^primary]

{% <figure page={page} src="equipment-placeholder.svg" alt='A "quote" & <em>literal</em>' caption="<em>literal</em>"> %}
Case courtesy of Example Author, <a href="https://example.com/images">Image library</a>. From the case <a href="https://example.com/cases/123">123</a>
{% </figure> %}

1. First action.
2. Second action.

{% <callout> %}
A source cited only inside a nested component.[^secondary]
{% </callout> %}
{% </step> %}

{% <step number={2} title="Finish the fixture"> %}
Check the result.
{% </step> %}

## References

[^primary]: First [source](https://example.com/source).

    A second paragraph of reference text.

[^secondary]: Second source.
[^unused]: An uncited definition is omitted.
''')
        starters = cls.site / "content/procedures/authoring-check"
        starters.mkdir()
        (starters / "_index.md").write_text('''+++
title = "Authoring check"
template = "family.html"
page_template = "article.html"
sort_by = "title"
+++
''')
        for kind in ("guide", "explainer"):
            bundle = starters / kind
            bundle.mkdir()
            shutil.copy2(ROOT / f"examples/{kind}.md", bundle / "index.md")
        shutil.copy2(ROOT / "examples/guide-figure.svg", starters / "guide")
        cls.run_zola("build", "--output-dir", "public")
        cls.run_zola("build", "--drafts", "--base-url", "https://example.test/handbook", "--output-dir", "drafts")

    @classmethod
    def run_zola(cls, *args):
        return subprocess.run(
            ["zola", "--root", str(cls.site), *args],
            cwd=cls.site, check=True, capture_output=True, text=True,
        )

    def test_public_build_excludes_drafts(self):
        self.assertFalse((self.site / "public/showcase/index.html").exists())
        self.assertFalse((self.site / "public/procedures/central-venous-access/migration-check/index.html").exists())
        home = Markup(self.site / "public/index.html")
        cards = [a["href"] for a in home.attrs("a") if "listing-card" in a.get("class", "")]
        self.assertIn("https://praxis.glfharris.com/procedures/central-venous-access/", cards)
        self.assertNotIn("https://praxis.glfharris.com/procedures/authoring-check/", cards,
                         "A family containing only draft starters must not appear on the homepage")
        for kind in ("guide", "explainer"):
            self.assertFalse((self.site / f"public/procedures/authoring-check/{kind}/index.html").exists())

    def test_components_and_recursive_toc(self):
        page = Markup(self.site / "drafts/procedures/central-venous-access/migration-check/index.html")
        self.assertEqual(page.attrs("em"), [], "Plain-text component arguments must stay escaped")
        label = 'A "quote" & <em>literal</em>'
        self.assertIn({"class": "callout callout--note", "aria-label": label}, page.attrs("aside"))
        self.assertIn({"class": "checklist", "aria-label": "Checklist"}, page.attrs("aside"))
        self.assertEqual(len(page.attrs("strong")), 2)
        self.assertIn("Second paragraph.", "".join(page.text))
        self.assertIn("Reviewer & colleague", "".join(page.text))
        figure = next(img for img in page.attrs("img") if img.get("src") == "equipment-placeholder.svg")
        self.assertEqual(figure["alt"], label)
        self.assertEqual(figure["width"], "960")
        self.assertEqual(figure["height"], "480")
        markup = (self.site / "drafts/procedures/central-venous-access/migration-check/index.html").read_text()
        caption = re.search(r"<figcaption>(.*?)</figcaption>", markup, re.S).group(1)
        self.assertIn('Case courtesy of Example Author,', caption)
        self.assertIn('<a href="https://example.com/images">Image library</a>', caption)
        self.assertIn('<a href="https://example.com/cases/123">123</a>', caption)
        ids = [attrs["id"] for _, attrs in page.tags if "id" in attrs]
        self.assertEqual(len(ids), len(set(ids)))
        child_links = [a["href"] for a in page.attrs("a") if a.get("href", "").endswith("#child-heading")]
        self.assertEqual(len(child_links), 2, "Desktop and mobile TOCs both include nested headings")
        self.assertTrue(all(url.startswith("https://example.test/handbook/") for url in child_links))

    def test_missing_kind_is_a_guide(self):
        family = Markup(self.site / "drafts/procedures/central-venous-access/index.html")
        text = " ".join("".join(family.text).split())
        self.assertIn("Practical guides · 2", text)
        self.assertIn("Supporting explanations · 3", text)
        home = Markup(self.site / "drafts/index.html")
        links = [a for a in home.attrs("a") if a.get("href", "").endswith("/migration-check/")]
        self.assertEqual(len(links), 1, "A guide without extra.kind gets a direct homepage link")

    def test_showcase_markup(self):
        page = Markup(self.site / "drafts/showcase/index.html")
        self.assertEqual(len(page.attrs("figure")), 3)
        self.assertEqual(len(page.attrs("details")), 2)
        self.assertEqual(len([a for a in page.attrs("aside") if "callout" in a.get("class", "")]), 6)
        self.assertEqual(page.attrs("pre"), [], "Component HTML must not become indented code blocks")

    def test_footnotes_share_numbering_and_return_links_across_components(self):
        page = Markup(self.site / "drafts/procedures/central-venous-access/migration-check/index.html")
        self.assertNotIn("[^", "".join(page.text), "Footnotes inside components must resolve")
        ids = [attrs["id"] for _, attrs in page.tags if "id" in attrs]
        self.assertEqual(len(ids), len(set(ids)), "Repeated citations need unique return targets")
        definitions = [attrs["id"] for attrs in page.attrs("li") if attrs.get("id", "").startswith("fn-")]
        self.assertEqual(definitions, ["fn-primary", "fn-secondary"])
        citations = [attrs for attrs in page.attrs("sup") if attrs.get("class") == "footnote-reference"]
        self.assertEqual(len(citations), 6)
        links = [attrs["href"] for attrs in page.attrs("a") if "href" in attrs]
        forward = [href for href in links if urlsplit(href).fragment.startswith("fn-")]
        backward = [href for href in links if urlsplit(href).fragment.startswith("fr-")]
        self.assertEqual(len(forward), 6)
        self.assertEqual([urlsplit(href).fragment for href in forward].count("fn-primary"), 5)
        self.assertEqual({urlsplit(href).fragment for href in backward}, {attrs["id"] for attrs in citations})
        self.assertEqual(len(backward), 6)
        self.assertTrue(all(href.startswith("https://example.test/handbook/") for href in forward + backward))

    def test_site_selection_citations_all_resolve(self):
        source = ROOT / "content/procedures/central-venous-access/choosing-a-site/index.md"
        article = source.read_text()
        expected = re.findall(r"\[\^([^\]]+)\](?!:)", article)
        definitions = re.findall(r"^\[\^([^\]]+)\]:", article, re.MULTILINE)
        page = Markup(self.site / "drafts/procedures/central-venous-access/choosing-a-site/index.html")
        self.assertNotIn("[^", "".join(page.text))
        self.assertEqual(len([a for a in page.attrs("sup") if a.get("class") == "footnote-reference"]), len(expected))
        entries = [a["id"] for a in page.attrs("li") if a.get("id", "").startswith("fn-")]
        self.assertEqual(entries, [f"fn-{label}" for label in dict.fromkeys(expected)])
        self.assertEqual(set(definitions), set(expected))

    def test_reference_return_links_are_grouped_without_losing_destinations(self):
        for relative_path in (
            "drafts/procedures/central-venous-access/migration-check/index.html",
            "public/procedures/central-venous-access/internal-jugular-cvc/index.html",
        ):
            with self.subTest(page=relative_path):
                path = self.site / relative_path
                page = Markup(path)
                html = path.read_text()
                references = [a for a in page.attrs("li") if a.get("id", "").startswith("fn-")]
                rows = re.findall(r'<p class="footnote-backlinks">(.*?)</p>', html, re.DOTALL)
                self.assertEqual(len(rows), len(references))
                self.assertTrue(all('>Cited at:</span>' in row for row in rows))
                citations = {a["id"] for a in page.attrs("sup") if a.get("class") == "footnote-reference"}
                backlinks = [a for a in page.attrs("a") if urlsplit(a.get("href", "")).fragment.startswith("fr-")]
                self.assertEqual({urlsplit(a["href"]).fragment for a in backlinks}, citations)
                for link in backlinks:
                    occurrence = urlsplit(link["href"]).fragment.rsplit("-", 1)[1]
                    self.assertEqual(link.get("aria-label"), f"Return to citation occurrence {occurrence}")
                    self.assertTrue(any(f'aria-label="Return to citation occurrence {occurrence}">{occurrence}</a>' in row for row in rows))
                self.assertNotIn("↩", "".join(page.text))
        fixture = Markup(self.site / "drafts/procedures/central-venous-access/migration-check/index.html")
        self.assertIn("A second paragraph of reference text.", "".join(fixture.text))
        self.assertTrue(any(a.get("href") == "https://example.com/source" for a in fixture.attrs("a")))

    def test_steps_are_headings_with_contents_links(self):
        path = self.site / "drafts/procedures/central-venous-access/migration-check/index.html"
        page = Markup(path)
        step_ids = [a["id"] for a in page.attrs("h3") if a.get("id", "").startswith("step-")]
        self.assertEqual(step_ids, ["step-1", "step-2"])
        for n in (1, 2):
            self.assertEqual(len([a for a in page.attrs("a") if a.get("href", "").endswith(f"#step-{n}")]), 2)
        self.assertEqual(page.attrs("pre"), [], "Step bodies must render as Markdown, not code")
        self.assertTrue(any(a.get("src", "").endswith("equipment-placeholder.svg") for a in page.attrs("img")))
        first_step = path.read_text().split('<h3 id="step-1">', 1)[1].split('<h3 id="step-2">', 1)[0]
        for markup in ('<figure', '<ol>', '<aside class="callout callout--note"'):
            self.assertIn(markup, first_step, "Steps must support figures, lists and nested callouts together")
        self.assertTrue(any("article.js" in a.get("src", "") and "defer" in a for a in page.attrs("script")))

    def test_authoring_starters_render_with_their_assets(self):
        guide = Markup(self.site / "drafts/procedures/authoring-check/guide/index.html")
        self.assertEqual([a["id"] for a in guide.attrs("h3")], ["step-1", "step-2"])
        figure = next(a for a in guide.attrs("img") if a.get("src") == "guide-figure.svg")
        self.assertEqual((figure["width"], figure["height"]), ("960", "480"))
        self.assertEqual(guide.attrs("pre"), [])
        self.assertEqual(len([a for a in guide.attrs("li") if a.get("id", "").startswith("fn-")]), 1)
        explainer = Markup(self.site / "drafts/procedures/authoring-check/explainer/index.html")
        self.assertEqual(len([a for a in explainer.attrs("li") if a.get("id", "").startswith("fn-")]), 1)

    def test_missing_image_fails_build(self):
        original = self.fixture.read_text()
        try:
            self.fixture.write_text(original.replace('src="equipment-placeholder.svg"', 'src="missing.svg"'))
            with self.assertRaises(subprocess.CalledProcessError) as error:
                self.run_zola("build", "--drafts", "--output-dir", "invalid")
            self.assertIn("missing.svg", error.exception.stderr + error.exception.stdout)
        finally:
            self.fixture.write_text(original)


if __name__ == "__main__":
    unittest.main()
