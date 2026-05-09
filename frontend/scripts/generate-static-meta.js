/* eslint-disable */
/**
 * Post-build SSG step.
 *
 * Reads frontend/build/index.html and writes one variant per static route
 * (12 zodiac landings, /pricing) with route-specific <title>, <meta
 * description>, og:*, twitter:*, canonical and JSON-LD baked into the HTML
 * head. Vercel's filesystem handler picks these up before the SPA
 * fallback, so non-JS crawlers (facebookexternalhit, linkedinbot,
 * slackbot, older twitterbot) see proper meta instead of the generic
 * site card.
 *
 * The React SPA still mounts on top and overwrites these tags with
 * the dated/live versions for users — only crawlers see the static stub.
 */

const fs = require('fs');
const path = require('path');

const buildDir = path.resolve(__dirname, '..', 'build');
const indexPath = path.join(buildDir, 'index.html');

if (!fs.existsSync(indexPath)) {
  console.error('[generate-static-meta] build/index.html not found — run craco build first');
  process.exit(1);
}

const baseHtml = fs.readFileSync(indexPath, 'utf8');

const SITE = 'https://gab44.com';
const DEFAULT_OG_IMAGE = `${SITE}/favicon.svg`;

const ZODIAC = {
  aries:       { name: 'Aries',       glyph: '♈', element: 'Fire',  ruler: 'Mars',     dates: 'March 21 - April 19' },
  taurus:      { name: 'Taurus',      glyph: '♉', element: 'Earth', ruler: 'Venus',    dates: 'April 20 - May 20' },
  gemini:      { name: 'Gemini',      glyph: '♊', element: 'Air',   ruler: 'Mercury',  dates: 'May 21 - June 20' },
  cancer:      { name: 'Cancer',      glyph: '♋', element: 'Water', ruler: 'Moon',     dates: 'June 21 - July 22' },
  leo:         { name: 'Leo',         glyph: '♌', element: 'Fire',  ruler: 'Sun',      dates: 'July 23 - August 22' },
  virgo:       { name: 'Virgo',       glyph: '♍', element: 'Earth', ruler: 'Mercury',  dates: 'August 23 - September 22' },
  libra:       { name: 'Libra',       glyph: '♎', element: 'Air',   ruler: 'Venus',    dates: 'September 23 - October 22' },
  scorpio:     { name: 'Scorpio',     glyph: '♏', element: 'Water', ruler: 'Pluto',    dates: 'October 23 - November 21' },
  sagittarius: { name: 'Sagittarius', glyph: '♐', element: 'Fire',  ruler: 'Jupiter',  dates: 'November 22 - December 21' },
  capricorn:   { name: 'Capricorn',   glyph: '♑', element: 'Earth', ruler: 'Saturn',   dates: 'December 22 - January 19' },
  aquarius:    { name: 'Aquarius',    glyph: '♒', element: 'Air',   ruler: 'Uranus',   dates: 'January 20 - February 18' },
  pisces:      { name: 'Pisces',      glyph: '♓', element: 'Water', ruler: 'Neptune',  dates: 'February 19 - March 20' },
};

function htmlEscape(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderHead({ title, description, url, ogType = 'website', jsonLd }) {
  const t = htmlEscape(title);
  const d = htmlEscape(description);
  const u = htmlEscape(url);
  const lines = [
    `<title>${t}</title>`,
    `<meta name="description" content="${d}" />`,
    `<link rel="canonical" href="${u}" />`,
    `<meta property="og:type" content="${ogType}" />`,
    `<meta property="og:title" content="${t}" />`,
    `<meta property="og:description" content="${d}" />`,
    `<meta property="og:url" content="${u}" />`,
    `<meta property="og:image" content="${DEFAULT_OG_IMAGE}" />`,
    `<meta property="og:site_name" content="Gab44" />`,
    `<meta name="twitter:card" content="summary" />`,
    `<meta name="twitter:title" content="${t}" />`,
    `<meta name="twitter:description" content="${d}" />`,
    `<meta name="twitter:image" content="${DEFAULT_OG_IMAGE}" />`,
  ];
  if (jsonLd) {
    lines.push(
      `<script type="application/ld+json">${JSON.stringify(jsonLd).replace(/</g, '\\u003c')}</script>`
    );
  }
  return lines.join('\n        ');
}

/**
 * Replace the default head meta block (description, og:*, twitter:*, title)
 * with the route-specific block. Other head content (favicon, fonts,
 * preload, OneSignal init) is preserved untouched.
 */
function rewriteHead(html, headBlock) {
  let out = html;
  // Strip the default tags we're going to override
  const stripPatterns = [
    /\s*<meta\s+name="description"[^>]*>/i,
    /\s*<meta\s+property="og:type"[^>]*>/i,
    /\s*<meta\s+property="og:title"[^>]*>/i,
    /\s*<meta\s+property="og:description"[^>]*>/i,
    /\s*<meta\s+property="og:url"[^>]*>/i,
    /\s*<meta\s+name="twitter:card"[^>]*>/i,
    /\s*<meta\s+name="twitter:title"[^>]*>/i,
    /\s*<meta\s+name="twitter:description"[^>]*>/i,
    /\s*<title>[^<]*<\/title>/i,
  ];
  for (const re of stripPatterns) out = out.replace(re, '');
  // Inject just before </head>
  out = out.replace(/<\/head>/i, `        ${headBlock}\n    </head>`);
  return out;
}

function writeRoute(relPath, html) {
  // Write both forms so Vercel's filesystem handler picks one up regardless
  // of trailing-slash behavior:
  //   /zodiac/leo       -> build/zodiac/leo.html
  //   /zodiac/leo/      -> build/zodiac/leo/index.html
  const folderTarget = path.join(buildDir, relPath, 'index.html');
  const flatTarget = path.join(buildDir, `${relPath}.html`);
  fs.mkdirSync(path.dirname(folderTarget), { recursive: true });
  fs.writeFileSync(folderTarget, html, 'utf8');
  fs.writeFileSync(flatTarget, html, 'utf8');
  console.log(
    `[generate-static-meta] wrote ${path.relative(buildDir, folderTarget)} + ${path.relative(buildDir, flatTarget)}`
  );
}

// ---- /zodiac/{slug} ----
for (const [slug, m] of Object.entries(ZODIAC)) {
  const url = `${SITE}/zodiac/${slug}`;
  const title = `${m.name} Daily Horoscope - Free Reading from Gab44`;
  const description = `${m.name} (${m.dates}) daily horoscope - love, career, wellness, lucky number and color. ${m.element} sign ruled by ${m.ruler}. Free reading refreshed every morning by AI astrologers.`;
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: title,
    description,
    author: { '@type': 'Organization', name: 'Gab44' },
    publisher: {
      '@type': 'Organization',
      name: 'Gab44',
      logo: { '@type': 'ImageObject', url: DEFAULT_OG_IMAGE },
    },
    mainEntityOfPage: url,
    about: { '@type': 'Thing', name: `${m.name} zodiac sign` },
  };
  const head = renderHead({ title, description, url, ogType: 'article', jsonLd });
  writeRoute(`zodiac/${slug}`, rewriteHead(baseHtml, head));
}

// ---- /pricing ----
{
  const url = `${SITE}/pricing`;
  const title = 'Pricing - Gab44 AI Astrology Coaching';
  const description = 'Choose your Gab44 plan: free Seeker access, $9.99/mo Enthusiast with 7-day free trial, $19.99/mo Advanced, or $29.99/mo Professional. Plus $19 personalized written readings.';
  const head = renderHead({ title, description, url, ogType: 'website' });
  writeRoute('pricing', rewriteHead(baseHtml, head));
}

console.log('[generate-static-meta] done');
