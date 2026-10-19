import { apiConfig, apiUrl, errorMessageFrom, requestJson } from '../client';
import { parseJob, type JobCreated } from '../contracts/inference';
import { InferenceError, type InferenceAdapter, type SlideInput, type SubmitOptions } from './InferenceAdapter';

/**
 * Talks to the model service (contract: ../contracts/inference.ts):
 *   POST   /jobs       multipart `slide` (.svs) [+ `case_id`] → 202 { job_id, status }
 *   GET    /jobs/:id   → { job_id, status, progress?, stage?, result?, error? }
 *   DELETE /jobs/:id   optional cancellation
 */
export const httpAdapter: InferenceAdapter = {
  mode: 'http',
  pollIntervalMs: 2_000,
  maxPollIntervalMs: 10_000,

  async submitJob(input, options) {
    const file = await fileFor(input, options.signal);
    const form = new FormData();
    form.append('slide', file, file.name);
    if (input.caseId) form.append('case_id', input.caseId);
    const body = await upload('/jobs', form, options);
    if (typeof body !== 'object' || body === null || typeof (body as JobCreated).job_id !== 'string') {
      throw new InferenceError('The model server accepted the upload but returned no job id.');
    }
    return body as JobCreated;
  },

  async getJob(jobId, { signal }) {
    return parseJob(await requestJson(`/jobs/${encodeURIComponent(jobId)}`, { signal }));
  },

  async cancelJob(jobId) {
    await requestJson(`/jobs/${encodeURIComponent(jobId)}`, { method: 'DELETE' }).catch(() => undefined);
  },
};

/** Sample slides aren't in the browser; the dev server exposes the .svs files at /sample-slides/. */
async function fileFor(input: SlideInput, signal: AbortSignal): Promise<File> {
  if (input.kind === 'file') return input.file;
  const res = await fetch(`/sample-slides/${encodeURIComponent(input.sourceFile)}`, { signal }).catch(() => null);
  if (!res?.ok || res.headers.get('content-type')?.includes('text/html')) {
    throw new InferenceError(
      `The sample .svs for ${input.sampleId} isn't served by this build. Upload the file with "browse files" instead.`,
    );
  }
  return new File([await res.blob()], input.sourceFile, { type: 'application/octet-stream' });
}

/** XHR rather than fetch, because fetch has no upload progress events. */
function upload(path: string, form: FormData, { signal, onUploadProgress }: SubmitOptions): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', apiUrl(path));
    xhr.responseType = 'json';
    xhr.setRequestHeader('Accept', 'application/json');

    xhr.upload.onprogress = (e) => onUploadProgress(e.loaded, e.lengthComputable ? e.total : null);
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) return resolve(xhr.response);
      reject(
        new InferenceError(
          errorMessageFrom(xhr.response, `Upload rejected by the model server (HTTP ${xhr.status}).`),
          {
            retryable: xhr.status >= 500,
          },
        ),
      );
    };
    xhr.onerror = () =>
      reject(new InferenceError(`Can't reach the model server at ${apiConfig.baseUrl}.`, { retryable: true }));
    xhr.onabort = () => reject(new DOMException('Upload cancelled', 'AbortError'));

    if (signal.aborted) return xhr.abort();
    signal.addEventListener('abort', () => xhr.abort(), { once: true });
    xhr.send(form);
  });
}
