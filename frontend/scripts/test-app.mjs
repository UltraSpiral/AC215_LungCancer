/** Actual Chromium -> nginx -> API -> saved classifier acceptance; no route mocking. */
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { copyFile, mkdir, readFile, writeFile, open } from 'node:fs/promises';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import path from 'node:path';

const exec = promisify(execFile);
const root = path.resolve(import.meta.dirname, '../..');
const bundle = path.resolve(process.env.LC_APP_BUNDLE ?? path.join(root, 'local_data/cpu_bundle'));
const base = process.env.LC_APP_URL ?? 'http://127.0.0.1:8080';
const output = path.resolve(process.env.LC_APP_EVIDENCE_DIR ?? path.join(root, 'local_outputs/app/browser'));
await mkdir(output, { recursive: true });
const classes = ['non_tumor', 'adenocarcinoma', 'squamous'];
const manifest = JSON.parse(await readFile(path.join(bundle, 'manifest.json'), 'utf8'));
const source = path.join(bundle, manifest.real_slide.path);
const model = JSON.parse(await readFile(path.join(bundle, 'run/model/model.json'), 'utf8'));
const references = JSON.parse(await readFile(path.join(bundle, 'run/evaluation_test/predictions.json'), 'utf8'));
const reference = references.find(r => r.file_id === manifest.real_slide.file_id);
assert.ok(reference);
const report = { status: 'running', started_at: new Date().toISOString(), base_url: base,
  scenarios: {}, requests: [], responses: [], page_errors: [], network_mocking_used: false,
  classifier_training_performed: false, uni2_encoding_performed: false };
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1050 }, deviceScaleFactor: 1 });
const page = await context.newPage();
page.setDefaultTimeout(30_000);
page.on('pageerror', error => report.page_errors.push(error.message));
page.on('request', request => {
  if (request.url().startsWith(base)) report.requests.push({ method: request.method(), url: request.url(), resource_type: request.resourceType() });
});
const created = [];
const pendingResponses = new Set();
page.on('response', response => {
  if (!response.url().startsWith(base + '/api/')) return;
  const pending = (async () => {
    const entry = { method: response.request().method(), url: response.url(), status: response.status() };
    if (response.headers()['content-type']?.includes('application/json')) entry.body = await response.json();
    report.responses.push(entry);
    if (entry.method === 'POST' && response.url() === base + '/api/jobs' && entry.status === 202) created.push(entry.body.job_id);
  })();
  pendingResponses.add(pending);
  pending.finally(() => pendingResponses.delete(pending));
});

async function screenshot(name) {
  await page.screenshot({ path: path.join(output, name + '.png'), fullPage: true });
}
async function finalJob(id) {
  for (let i = 0; i < 100; i++) {
    const response = await context.request.get(base + '/api/jobs/' + id);
    assert.equal(response.status(), 200);
    const job = await response.json();
    if (job.status === 'done' || job.status === 'failed') return job;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error('Job did not reach a terminal state');
}
function verifyResult(result) {
  assert.equal(result.status, 'success');
  assert.equal(result.model_identifier, model.model_identifier);
  assert.equal(result.tiles_analyzed, 512);
  assert.equal(result.probabilities_calibrated, false);
  assert.equal(result.uni2_encoding_performed, false);
  for (const c of classes) assert.ok(Math.abs(result.class_probabilities[c] - reference.class_probabilities[c]) <= 1e-8);
}
async function select(file) {
  await page.getByLabel('Upload a .svs slide').setInputFiles(file);
}
async function runSuccess(file, name) {
  const count = created.length;
  await select(file);
  await page.getByRole('button', { name: 'Analyse slide', exact: true }).click();
  await page.locator('[data-class]').waitFor({ state: 'visible' });
  await Promise.all([...pendingResponses]);
  assert.equal(created.length, count + 1);
  const job = await finalJob(created.at(-1));
  verifyResult(job.result);
  assert.equal(await page.locator('[data-class]').getAttribute('data-class'), job.result.predicted_class);
  assert.equal(await page.getByText('512', { exact: true }).count(), 1);
  const overlay = page.getByAltText('Actual supplied slide with previously analyzed tile locations');
  await overlay.waitFor({ state: 'visible' });
  await page.waitForFunction(() => document.querySelector('figure img')?.naturalWidth > 0);
  await screenshot(name);
  await writeFile(path.join(output, name + '.json'), JSON.stringify(job, null, 2));
  assert.ok(report.responses.some(r => r.method === 'GET' && r.url === base + '/api/jobs/' + job.job_id));
  report.scenarios[name] = { status: 'success', job_id: job.job_id, result: job.result };
  return job.result;
}

const env = { ...process.env, LC_APP_UID: String(process.getuid()), LC_APP_GID: String(process.getgid()) };
let apiStopped = false;
try {
  const health = await context.request.get(base + '/api/health');
  assert.equal(health.status(), 200);
  assert.equal((await health.json()).processing_mode, 'preprocessed_slide_demo');
  await page.goto(base + '/kitchen-sink?sample=TCGA-05-4244', { waitUntil: 'networkidle' });
  assert.ok(await page.getByText('Preprocessed-slide demo', { exact: true }).count() > 0);
  assert.equal(await page.locator('[data-class]').count(), 0);
  report.scenarios.fixture_routes_isolated = { status: 'success', no_preselected_fixture: true };
  await page.goto(base, { waitUntil: 'networkidle' });
  assert.ok(await page.getByText('Preprocessed-slide demo', { exact: true }).count() > 0);
  assert.equal(await page.getByText(/Sample slides ·/).count(), 0);
  await screenshot('ready');
  const first = await runSuccess(source, 'known-result');

  await page.getByRole('button', { name: 'Analyse another slide' }).click();
  const renamed = path.join(output, 'TCGA-FAKE-LUAD-Primary-Tumor.svs');
  await copyFile(source, renamed);
  const second = await runSuccess(renamed, 'renamed-result');
  assert.deepEqual(second.class_probabilities, first.class_probabilities);
  assert.equal(second.source_sha256, first.source_sha256);
  report.scenarios.renamed_filename_invariance = { status: 'success', probability_difference: 0 };

  // Metadata-spoof check hits the running container through real HTTP, without browser interception.
  const bytes = await readFile(source);
  const spoof = await context.request.post(base + '/api/jobs', { multipart: {
    slide: { name: 'squamous-diagnosis.svs', mimeType: 'application/octet-stream', buffer: bytes },
    case_id: 'adenocarcinoma-tumor-project-misleading-metadata',
  } });
  assert.equal(spoof.status(), 202);
  const spoofJob = await finalJob((await spoof.json()).job_id);
  verifyResult(spoofJob.result);
  assert.deepEqual(spoofJob.result.class_probabilities, first.class_probabilities);
  report.scenarios.misleading_case_metadata = { status: 'success', job: spoofJob };

  const modified = Buffer.from(bytes); modified[modified.length - 1] ^= 1;
  const changed = await context.request.post(base + '/api/jobs', { multipart: {
    slide: { name: 'sample.svs', mimeType: 'application/octet-stream', buffer: modified },
  } });
  assert.equal(changed.status(), 202);
  const changedJob = await finalJob((await changed.json()).job_id);
  assert.equal(changedJob.status, 'failed'); assert.equal(changedJob.result, undefined);
  report.scenarios.modified_slide = { status: 'success', job: changedJob };

  await page.getByRole('button', { name: 'Analyse another slide' }).click();
  const unknown = path.join(output, 'sample.svs');
  await writeFile(unknown, 'Unknown unprocessed slide content; never a synthetic model input.');
  await select(unknown);
  await page.getByRole('button', { name: 'Analyse slide', exact: true }).click();
  await page.getByRole('heading', { name: 'Analysis failed', exact: true }).waitFor();
  assert.equal(await page.locator('[data-class]').count(), 0);
  assert.ok(await page.getByText(/Unsupported slide: no verified/).count());
  const unknownJob = await finalJob(created.at(-1));
  assert.equal(unknownJob.status, 'failed'); assert.equal(unknownJob.result, undefined);
  await screenshot('unknown-error');
  report.scenarios.unknown_slide = { status: 'success', job: unknownJob };

  await page.getByRole('button', { name: 'Change slide' }).click();
  await select({ name: 'empty.svs', mimeType: 'application/octet-stream', buffer: Buffer.alloc(0) });
  assert.equal(await page.getByRole('alert').textContent(), 'The selected slide is empty.');
  assert.equal(await page.getByRole('button', { name: 'Analyse slide', exact: true }).count(), 0);
  await screenshot('empty-error');
  report.scenarios.empty_upload = { status: 'success', no_prediction: true };

  const oversized = path.join(output, 'oversized.svs');
  const handle = await open(oversized, 'w'); await handle.truncate(80_000_001); await handle.close();
  await select(oversized);
  assert.equal(await page.getByRole('alert').textContent(), 'The demo upload limit is 80 MB.');
  assert.equal(await page.locator('[data-class]').count(), 0);
  await screenshot('oversized-error');
  report.scenarios.oversized_upload = { status: 'success', no_prediction: true };

  await exec('docker', ['compose', '-f', 'compose.app.yml', 'stop', 'api'], { cwd: root, env });
  apiStopped = true;
  await select(source);
  await page.getByRole('button', { name: 'Analyse slide', exact: true }).click();
  await page.getByRole('heading', { name: 'Upload failed', exact: true }).waitFor();
  assert.ok(await page.getByText('The model service is unavailable. Start the app and try again.').count());
  assert.equal(await page.locator('[data-class]').count(), 0);
  await screenshot('backend-unavailable');
  report.scenarios.backend_unavailable = { status: 'success', no_prediction: true, actual_api_container_stopped: true };
  assert.equal(report.page_errors.length, 0);
  assert.ok(report.requests.every(r => !r.url.includes('/slides/') && !r.url.includes('/sample-slides/')));
  report.status = 'success';
} catch (error) {
  report.status = 'error'; report.error = String(error.stack ?? error);
  await screenshot('failure').catch(() => {});
  throw error;
} finally {
  if (apiStopped) {
    const resumed = await exec('docker', ['compose', '-f', 'compose.app.yml', 'up', '-d', '--wait', '--wait-timeout', '120', 'api'], { cwd: root, env });
    await writeFile(path.join(output, 'api-resume.log'), resumed.stdout + resumed.stderr);
    report.api_resumed = true;
    assert.equal((await context.request.get(base + '/api/health')).status(), 200);
  }
  await Promise.allSettled([...pendingResponses]);
  report.finished_at = new Date().toISOString();
  await writeFile(path.join(output, 'browser-report.json'), JSON.stringify(report, null, 2));
  await browser.close();
}
console.log(JSON.stringify({ status: report.status, scenarios: Object.keys(report.scenarios), report: path.join(output, 'browser-report.json') }, null, 2));
