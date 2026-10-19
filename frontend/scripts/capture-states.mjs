// Screenshot every Review-screen state in mock mode at the Figma frame size (1440×1061).
// Usage: start `npm run dev` (mock mode), then: node scripts/capture-states.mjs [baseUrl] [outDir]
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const base = process.argv[2] ?? 'http://localhost:5173';
const out = path.resolve(process.argv[3] ?? 'docs/screenshots');
mkdirSync(out, { recursive: true });

const SAMPLES = ['TCGA-91-8496', 'TCGA-52-7810', 'TCGA-38-7271'];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 1061 } });
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));

const panel = page.locator('aside');
const shot = async (name) => {
  await page.waitForTimeout(350); // let OSD finish blending tiles
  await page.screenshot({ path: path.join(out, `${name}.png`) });
  console.log(`  ${name}.png`);
};
const waitForPanel = (text, timeout = 30_000) => panel.getByText(text, { exact: false }).first().waitFor({ timeout });

await page.goto(`${base}/`, { waitUntil: 'networkidle' });
await shot('00-idle-empty');

for (const [i, id] of SAMPLES.entries()) {
  const n = String(i + 1);
  await page.goto(`${base}/?sample=${id}`, { waitUntil: 'networkidle' });
  await shot(`${n}0-${id}-idle`);
  await page.getByRole('button', { name: 'Analyse slide' }).click();
  if (i === 0) {
    await waitForPanel('Uploading');
    await shot(`${n}1-${id}-uploading`);
    await waitForPanel('Starting');
    await shot(`${n}2-${id}-queued`);
    await waitForPanel('Step 2 of 2 · Analysing');
    await page.waitForTimeout(2500);
    await shot(`${n}3-${id}-analysing`);
  }
  await waitForPanel('Predicted class', 60_000);
  await shot(`${n}4-${id}-result`);
  if (i === 0) {
    // Zoomed-in result, to show tiles, minimap box and magnification readout.
    for (let k = 0; k < 3; k++) {
      await page.getByRole('button', { name: 'Zoom in' }).click();
      await page.waitForTimeout(500);
    }
    await page.waitForLoadState('networkidle');
    await shot(`${n}5-${id}-result-zoomed`);
  }
}

// Error: any non-sample upload resolves to the error fixture in mock mode.
await page.goto(`${base}/`, { waitUntil: 'networkidle' });
await page.setInputFiles('input[type=file]', {
  name: 'LH-2026-0430-unknown.svs',
  mimeType: 'application/octet-stream',
  buffer: Buffer.alloc(2_000_000, 1),
});
await shot('40-upload-no-preview-idle');
await page.getByRole('button', { name: 'Analyse slide' }).click();
await waitForPanel('No prediction', 60_000);
await shot('41-error');

await page.goto(`${base}/kitchen-sink`, { waitUntil: 'networkidle' });
await page.screenshot({ path: path.join(out, '90-kitchen-sink.png'), fullPage: true });
console.log('  90-kitchen-sink.png');

await browser.close();
if (errors.length) {
  console.error('page errors:', errors);
  process.exit(1);
}
