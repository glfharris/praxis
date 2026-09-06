import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { runInNewContext } from 'node:vm';

const source = readFileSync(new URL('../static/article.js', import.meta.url), 'utf8');

function browser(scrollY = 0) {
  const events = new Map();
  const window = { scrollY, innerHeight: 800, addEventListener: (name, fn) => events.set(name, fn) };
  const ids = ['overview', 'step-1', 'rising-dough', 'finish'];
  const headings = ids.map((id, i) => ({ id, getBoundingClientRect: () => ({ top: 400 + i * 500 - window.scrollY }) }));
  const links = [...ids, ...ids].map(id => ({
    href: `https://example.test/guide/#${id}`,
    attrs: {},
    setAttribute(name, value) { this.attrs[name] = value; },
    removeAttribute(name) { delete this.attrs[name]; },
  }));
  const document = {
    documentElement: { scrollHeight: 2400 },
    querySelectorAll: () => links,
    getElementById: id => headings.find(h => h.id === id),
    addEventListener: (name, fn) => events.set(name, fn),
  };
  runInNewContext(source, { window, document, URL, requestAnimationFrame: fn => fn() });
  return {
    window,
    events,
    active: () => links.filter(l => l.attrs['aria-current'] === 'location').map(l => new URL(l.href).hash),
    scroll: y => { window.scrollY = y; events.get('scroll')(); },
  };
}

test('highlights one link in each contents list and follows scrolling in both directions', () => {
  const page = browser();
  assert.deepEqual(page.active(), ['#overview', '#overview']);
  page.scroll(850);
  assert.deepEqual(page.active(), ['#step-1', '#step-1']);
  page.scroll(1350);
  assert.deepEqual(page.active(), ['#rising-dough', '#rising-dough']);
  page.scroll(0);
  assert.deepEqual(page.active(), ['#overview', '#overview']);
});

test('recognises a restored scroll position and a short final section', () => {
  const page = browser(850);
  assert.deepEqual(page.active(), ['#step-1', '#step-1']);
  page.scroll(1600);
  assert.deepEqual(page.active(), ['#finish', '#finish']);
});

test('updates after anchor navigation, disclosures and history restoration', () => {
  const page = browser();
  page.window.scrollY = 1350;
  page.events.get('hashchange')();
  assert.deepEqual(page.active(), ['#rising-dough', '#rising-dough']);
  page.window.scrollY = 850;
  page.events.get('toggle')();
  assert.deepEqual(page.active(), ['#step-1', '#step-1']);
  page.window.scrollY = 0;
  page.events.get('pageshow')();
  assert.deepEqual(page.active(), ['#overview', '#overview']);
});

test('does nothing when there are no contents links', () => {
  runInNewContext(source, { document: { querySelectorAll: () => [] } });
});
