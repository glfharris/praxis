"""Build-level migration checks. Run with: python3 tests/check_site.py"""

from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


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

{% <callout kind="unknown" title='A "quote" & <em>literal</em>'> %}
First **strong** paragraph with a [link](https://example.com/).

Second paragraph.
{% </callout> %}

{% <checklist> %}
- Outer item
  - Nested item
{% </checklist> %}

{% <details title='A "quote" & <em>literal</em>'> %}
Optional **detail**.
{% </details> %}

{{ <figure page={page} src="equipment-placeholder.svg" alt='A "quote" & <em>literal</em>' caption="<em>literal</em>" /> }}
''')
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
        self.assertEqual(cards, ["https://praxis.glfharris.com/procedures/baking-bread/"])

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
        ids = [attrs["id"] for _, attrs in page.tags if "id" in attrs]
        self.assertEqual(len(ids), len(set(ids)))
        child_links = [a["href"] for a in page.attrs("a") if a.get("href", "").endswith("#child-heading")]
        self.assertEqual(len(child_links), 2, "Desktop and mobile TOCs both include nested headings")
        self.assertTrue(all(url.startswith("https://example.test/handbook/") for url in child_links))

    def test_missing_kind_is_a_guide(self):
        family = Markup(self.site / "drafts/procedures/central-venous-access/index.html")
        text = " ".join("".join(family.text).split())
        self.assertIn("Practical guides · 2", text)
        self.assertIn("Supporting explanations · 1", text)
        home = Markup(self.site / "drafts/index.html")
        links = [a for a in home.attrs("a") if a.get("href", "").endswith("/migration-check/")]
        self.assertEqual(len(links), 1, "A guide without extra.kind gets a direct homepage link")

    def test_showcase_markup(self):
        page = Markup(self.site / "drafts/showcase/index.html")
        self.assertEqual(len(page.attrs("figure")), 3)
        self.assertEqual(len(page.attrs("details")), 2)
        self.assertEqual(len([a for a in page.attrs("aside") if "callout" in a.get("class", "")]), 6)
        self.assertEqual(page.attrs("pre"), [], "Component HTML must not become indented code blocks")

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
