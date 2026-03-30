/**
 * Normalize job posting URLs for use in <a href>.
 * Scheme-less URLs (e.g. "linkedin.com/jobs/...") are resolved relative to the
 * current page origin, so they incorrectly open under localhost.
 */
export function normalizeJobPostingUrl(raw) {
  if (raw == null) return null;
  const s = String(raw).trim();
  if (!s) return null;
  if (/^javascript:/i.test(s) || /^data:/i.test(s)) return null;
  if (/^https?:\/\//i.test(s)) return s;
  if (s.startsWith('//')) return `https:${s}`;
  // Path-only: browser would resolve against localhost
  if (s.startsWith('/')) {
    if (
      s.startsWith('/jobs/view') ||
      s.startsWith('/jobs/search') ||
      s.startsWith('/jobs/collections')
    ) {
      return `https://www.linkedin.com${s}`;
    }
    return `https://boards.greenhouse.io${s}`;
  }
  return `https://${s}`;
}
