// Navigation remains ordinary anchor links when JavaScript is unavailable.
(() => {
  const links = [...document.querySelectorAll('.desktop-toc a, .mobile-toc a')];
  const byHeading = new Map();
  for (const link of links) {
    const id = decodeURIComponent(new URL(link.href).hash.slice(1));
    const heading = document.getElementById(id);
    if (!heading) continue;
    if (!byHeading.has(heading)) byHeading.set(heading, []);
    byHeading.get(heading).push(link);
  }
  const headings = [...byHeading.keys()];
  if (!headings.length) return;
  let active;
  let scheduled = false;

  function update() {
    scheduled = false;
    const threshold = Math.min(120, window.innerHeight * 0.2);
    let current = headings[0];
    for (const heading of headings) {
      if (heading.getBoundingClientRect().top > threshold) break;
      current = heading;
    }
    // Short final sections may never reach the activation line.
    if (window.scrollY > 0 && window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) {
      current = headings[headings.length - 1];
    }
    if (current === active) return;
    if (active) for (const link of byHeading.get(active)) link.removeAttribute('aria-current');
    for (const link of byHeading.get(current)) link.setAttribute('aria-current', 'location');
    active = current;
  }

  function scheduleUpdate() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(update);
  }
  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', scheduleUpdate);
  window.addEventListener('hashchange', scheduleUpdate);
  window.addEventListener('pageshow', scheduleUpdate);
  document.addEventListener('toggle', scheduleUpdate, true);
  // Images and disclosures can move headings without a scroll event.
  if ('ResizeObserver' in window) new ResizeObserver(scheduleUpdate).observe(document.querySelector('.article-body'));
  update();
})();
