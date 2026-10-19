// Usage: node shot.mjs <url> <out.png> [width] [height]
import { chromium } from 'playwright';
const [, , url, out, w = '1440', h = '1061'] = process.argv;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
await page.goto(url, { waitUntil: 'networkidle' });
await page.waitForTimeout(500);
await page.screenshot({ path: out, fullPage: true });
await browser.close();
