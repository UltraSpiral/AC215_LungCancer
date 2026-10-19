// Measure key elements of the Review screen (result state, 1440×1061) and diff them with the
// absolute positions of the matching layers in Figma Screen 2 (coordinates below were measured from the design file).
// Usage: node scripts/compare-figma.mjs [baseUrl] > docs/figma-measurements.md
import { chromium } from 'playwright';

const base = process.argv[2] ?? 'http://localhost:5173';

// [label, figma {x,y,w,h} in Screen 2 coordinates, how to find it in the DOM]
// Figma values = sum of @x,y offsets down the tree from "Screen 2".
const TARGETS = [
  ['Header brand mark', { x: 24, y: 23, w: 22, h: 22 }, (p) => p.locator('header span[aria-hidden]').first()],
  ['Segmented nav', { x: 586.3, y: 12.5, w: 267.4, h: 43 }, (p) => p.getByRole('navigation', { name: 'Sections' })],
  ['Nav · active "Review"', { x: 688.6, y: 17.5, w: 80.1, h: 33 }, (p) => p.getByRole('button', { name: 'Review' })],
  ['Case strip', { x: 24, y: 72, w: 1392, h: 68 }, (p) => p.getByLabel('Case details')],
  ['Case id text', { x: 49, y: 93, w: 141.6, h: 26 }, (p) => p.getByRole('heading', { level: 1 })],
  [
    'Case fields (first)',
    { x: 222.6, y: 89, w: 116.6, h: 34 },
    (p) => p.getByLabel('Case details').locator('dl > div').first(),
  ],
  ['Priority chip', { x: 1194.4, y: 92, w: 95.5, h: 28 }, (p) => p.getByText('Urgent · 48 h')],
  [
    'Viewer card',
    { x: 24, y: 156, w: 1014, h: 881.4 },
    (p) => p.locator('main > div > div').first().locator('> section'),
  ],
  ['Panel card', { x: 1054, y: 156, w: 362, h: 881.4 }, (p) => p.locator('aside > section')],
  ['Zoom pill', { x: 248, y: 171, w: 136, h: 38 }, (p) => p.getByRole('group', { name: 'Zoom' })],
  ['Fit button', { x: 398, y: 172.5, w: 45.2, h: 35 }, (p) => p.getByRole('button', { name: 'Fit' })],
  ['Slide pane', { x: 41, y: 221, w: 980, h: 640 }, (p) => p.getByLabel('Slide image').locator('..')],
  [
    'Pane label "Original"',
    { x: 53, y: 233, w: 95.3, h: 28 },
    (p) => p.getByText('Original', { exact: true }).locator('..'),
  ],
  [
    'Minimap',
    { x: 53, y: 749.4, w: 133.4, h: 99.6 },
    (p) => p.locator('img[src$="thumbnail.jpg"]').first().locator('../..'),
  ],
  ['Caption line 1', { x: 41, y: 876, w: 253.9, h: 20 }, (p) => p.getByText(/objective/)],
  ['Panel title "AI analysis"', { x: 1075, y: 177.5, w: 69.5, h: 17 }, (p) => p.locator('aside h2')],
  ['Eyebrow above class', { x: 1075, y: 217, w: 320, h: 16 }, (p) => p.getByText('Predicted class', { exact: true })],
  ['Class headline', { x: 1075, y: 239, w: 320, h: 53.4 }, (p) => p.locator('aside h3')],
  [
    'Stat numeral',
    { x: 1075, y: 310.4, w: 154, h: 52 },
    (p) => p.getByText('Tiles analysed').locator('..').locator('p').first(),
  ],
  ['Action bar', { x: 1055, y: 959.4, w: 360, h: 77 }, (p) => p.locator('aside footer')],
];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1061 } });
await page.goto(`${base}/?sample=TCGA-91-8496`, { waitUntil: 'networkidle' });
await page.getByRole('button', { name: 'Analyse slide' }).click();
await page.getByText('Predicted class').waitFor({ timeout: 60_000 });

const fmt = (n) => (Math.round(n * 10) / 10).toString();
const rows = [];
for (const [label, f, find] of TARGETS) {
  const box = await find(page).first().boundingBox();
  if (!box) {
    rows.push(`| ${label} | ${fmt(f.x)}, ${fmt(f.y)} · ${fmt(f.w)}×${fmt(f.h)} | not found | | |`);
    continue;
  }
  const d = [box.x - f.x, box.y - f.y, box.width - f.w, box.height - f.h];
  const worst = Math.max(...d.map(Math.abs));
  const flag = worst <= 2 ? '✓' : worst <= 6 ? '≈' : '✗';
  rows.push(
    `| ${label} | ${fmt(f.x)}, ${fmt(f.y)} · ${fmt(f.w)}×${fmt(f.h)} | ${fmt(box.x)}, ${fmt(box.y)} · ${fmt(box.width)}×${fmt(box.height)} | ${d.map(fmt).join(' / ')} | ${flag} |`,
  );
}
// Typography: [label, Figma "family weight size/lh color tracking", locator]
const TYPE = [
  ['Role label', 'Geist 400 13 #8A909B', (p) => p.getByText('Remote Pathologist')],
  ['Nav tab (inactive)', 'Geist 400 13 #4B515C', (p) => p.getByRole('button', { name: 'Queue · 11' })],
  ['Nav tab (active)', 'Geist 500 13 #FFFFFF', (p) => p.getByRole('button', { name: 'Review' })],
  ['Case id', 'Geist Mono 500 20 #161A21 -0.2px', (p) => p.getByRole('heading', { level: 1 })],
  ['Case field label', 'Geist 400 11 #697080', (p) => p.getByText('Specimen', { exact: true })],
  ['Case field value', 'Geist 400 14 #161A21', (p) => p.getByText('Ridgeway Rural Clinic')],
  ['Priority chip', 'Geist 500 12 #8A5200', (p) => p.getByText('Urgent · 48 h')],
  ['Zoom readout', 'Geist Mono 500 15 #161A21', (p) => p.getByRole('status', { name: 'Magnification' })],
  ['Pane label', 'Geist 500 12 #161A21', (p) => p.getByText('Original', { exact: true })],
  ['Caption', 'Geist 400 12 #697080', (p) => p.getByText(/objective/)],
  ['Panel title', 'Geist 600 13 #161A21', (p) => p.locator('aside h2')],
  ['Model id', 'Geist 400 13 #8A909B', (p) => p.locator('aside h2 span')],
  ['Eyebrow', 'Geist 400 12 #697080', (p) => p.getByText('Predicted class', { exact: true })],
  ['Class headline', 'Geist 500 22 #161A21 -0.44px', (p) => p.locator('aside h3')],
  [
    'Stat numeral',
    'Geist 300 52 #161A21 -2.34px',
    (p) => p.getByText('Tiles analysed').locator('..').locator('p').first(),
  ],
  ['Section title', 'Geist 400 12 #697080', (p) => p.getByText(/^Quality warnings/)],
  ['Secondary button', 'Geist 400 14 #161A21', (p) => p.getByRole('button', { name: 'Analyse another slide' })],
];
const hex = (rgb) => {
  const m = rgb.match(/\d+(\.\d+)?/g)?.map(Number) ?? [];
  return (
    '#' +
    m
      .slice(0, 3)
      .map((v) => Math.round(v).toString(16).padStart(2, '0'))
      .join('')
      .toUpperCase()
  );
};
const typeRows = [];
for (const [label, figma, find] of TYPE) {
  const el = find(page).first();
  const st = await el.evaluate((n) => {
    const c = getComputedStyle(n);
    return { family: c.fontFamily, weight: c.fontWeight, size: c.fontSize, color: c.color, ls: c.letterSpacing };
  });
  const family = st.family.split(',')[0].replace(/['"]/g, '');
  const ls = st.ls === 'normal' ? '' : ` ${st.ls}`;
  const built = `${family} ${st.weight} ${parseFloat(st.size)} ${hex(st.color)}${ls}`;
  typeRows.push(`| ${label} | ${figma} | ${built} | ${built === figma ? '✓' : '✗'} |`);
}
await browser.close();

console.log('### Geometry (result state, TCGA-91-8496, viewport 1440×1061)\n');
console.log('| Element | Figma x, y · w×h | Build x, y · w×h | Δ x / y / w / h | |');
console.log('| --- | --- | --- | --- | --- |');
console.log(rows.join('\n'));
console.log('\n### Typography & colour\n');
console.log('| Element | Figma | Build (computed) | |');
console.log('| --- | --- | --- | --- |');
console.log(typeRows.join('\n'));
