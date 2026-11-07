"""Bounded, local-only HTTP jobs for the saved cached-feature classifier."""
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import asyncio
import hashlib
import json
import os
import tempfile
import threading
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.model import CachedClassifier, MODEL_ID, SNAPSHOT_ID, UnsupportedSlide
from lungcancer.common import atomic_json, utcnow

MAX_FILE_BYTES = 80_000_000
MAX_REQUEST_BYTES = 82_000_000


class BoundedUpload:
    """Spool a bounded multipart stream before parsing; never buffer a slide in RAM."""
    def __init__(self, app):
        self.app = app
        self.upload_active = False

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST' or scope['path'] != '/jobs':
            return await self.app(scope, receive, send)
        if self.upload_active:
            return await JSONResponse({'status': 'error', 'reason': 'Another slide is uploading. Try again shortly.'},
                                      status_code=429)(scope, receive, send)
        self.upload_active = True
        try:
            await self.upload(scope, receive, send)
        finally:
            self.upload_active = False

    async def upload(self, scope, receive, send):
        headers = dict(scope['headers'])
        async def reject(code, reason):
            await JSONResponse({'status': 'error', 'reason': reason}, status_code=code)(scope, receive, send)
        if not headers.get(b'content-type', b'').lower().startswith(b'multipart/form-data;'):
            return await reject(415, 'Upload one .svs file as multipart field slide.')
        try:
            length = int(headers.get(b'content-length', b'0'))
            if length < 0:
                raise ValueError()
        except ValueError:
            return await reject(400, 'Invalid upload length.')
        if length > MAX_REQUEST_BYTES:
            return await reject(413, 'Upload too large. The demo limit is 80 MB per slide.')
        with tempfile.SpooledTemporaryFile(max_size=1_000_000) as body:
            total = 0
            try:
                async with asyncio.timeout(60):
                    while True:
                        message = await receive()
                        if message['type'] == 'http.disconnect':
                            return
                        chunk = message.get('body', b'')
                        total += len(chunk)
                        if total > MAX_REQUEST_BYTES:
                            return await reject(413, 'Upload too large. The demo limit is 80 MB per slide.')
                        body.write(chunk)
                        if not message.get('more_body', False):
                            break
            except TimeoutError:
                return await reject(408, 'Upload timed out. Try again with the supplied slide.')
            body.seek(0)
            async def replay():
                chunk = body.read(1024 * 1024)
                return {'type': 'http.request', 'body': chunk, 'more_body': body.tell() < total}
            await self.app(scope, replay, send)


class Jobs:
    def __init__(self, model, output):
        self.model = model
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.model.create_overlay(self.output / 'analyzed_tiles_overlay.jpg')
        self.lock = threading.RLock()
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='cached-classifier')
        self.records = {}

    def save(self, job):
        atomic_json(self.output / (job['job_id'] + '.json'), job)

    def submit(self, identity):
        with self.lock:
            if sum(j['status'] in {'queued', 'running'} for j in self.records.values()) >= 4:
                raise HTTPException(429, 'The demo is busy. Wait for the current jobs to finish.')
            # Retain the latest 100 job envelopes in memory; disk evidence is preserved.
            if len(self.records) >= 100:
                oldest = next(k for k, j in self.records.items() if j['status'] in {'done', 'failed'})
                del self.records[oldest]
            key = uuid.uuid4().hex
            job = {'job_id': key, 'status': 'queued', 'stage': 'Waiting to verify cached features',
                   'created_at': utcnow(), 'processing_mode': 'preprocessed_slide_demo'}
            self.records[key] = job
            self.save(job)
            self.pool.submit(self.run, key, identity)
            return {'job_id': key, 'status': 'queued'}

    def run(self, key, identity):
        with self.lock:
            job = self.records[key]
            if job['status'] == 'failed':
                return
            job.update(status='running', stage='Verifying cached features and applying the saved classifier')
            self.save(job)
        try:
            result = self.model.predict(*identity)
            result['analyzed_tiles_overlay'] = f'/api/jobs/{key}/overlay'
            with self.lock:
                if job['status'] == 'failed':
                    return
                job.update(status='done', stage='Complete', result=result, finished_at=utcnow())
        except UnsupportedSlide as exc:
            with self.lock:
                if job['status'] != 'failed':
                    job.update(status='failed', error=str(exc), reason='unsupported_slide', finished_at=utcnow())
        except Exception:
            with self.lock:
                if job['status'] != 'failed':
                    job.update(status='failed', error='The saved model or cached features could not be verified. '
                               'No prediction was produced.', reason='cached_input_verification_failed', finished_at=utcnow())
        with self.lock:
            self.save(job)
            print(json.dumps({'event': 'job_finished', 'job_id': key, 'status': job['status']}), flush=True)

    def get(self, key):
        with self.lock:
            if key not in self.records:
                raise HTTPException(404, 'Job not found. Jobs from an earlier app session are not resumed.')
            return dict(self.records[key])

    def cancel(self, key):
        with self.lock:
            job = self.records.get(key)
            if job is None:
                raise HTTPException(404, 'Job not found.')
            if job['status'] in {'queued', 'running'}:
                job.update(status='failed', error='Analysis cancelled. No prediction was produced.',
                           reason='cancelled', finished_at=utcnow())
                self.save(job)
            return dict(job)


def create_app(bundle=None, output=None, model_factory=CachedClassifier):
    @asynccontextmanager
    async def lifespan(api):
        model = model_factory(Path(bundle or os.environ.get('LC_APP_BUNDLE', '/inputs')))
        jobs = Jobs(model, Path(output or os.environ.get('LC_APP_OUTPUT', '/work/jobs')))
        api.state.jobs = jobs
        print(json.dumps({'event': 'verified_model_ready', 'model_identifier': MODEL_ID,
                          'data_snapshot_identifier': SNAPSHOT_ID, 'uni2_encoding_performed': False}), flush=True)
        yield
        jobs.pool.shutdown(wait=True, cancel_futures=True)

    api = FastAPI(title='Preprocessed-slide demo', lifespan=lifespan, docs_url=None, redoc_url=None)

    @api.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        return JSONResponse({'status': 'error', 'reason': str(exc.detail)}, status_code=exc.status_code)

    @api.get('/health')
    def health():
        return {'status': 'ready', 'processing_mode': 'preprocessed_slide_demo', 'model_identifier': MODEL_ID,
                'data_snapshot_identifier': SNAPSHOT_ID, 'supported_slides': 1, 'uni2_encoding_performed': False}

    @api.post('/jobs', status_code=202)
    async def submit(request: Request):
        async with request.form(max_files=1, max_fields=1, max_part_size=4096) as form:
            files = form.getlist('slide')
            if len(files) != 1 or not isinstance(files[0], UploadFile):
                raise HTTPException(400, 'Upload exactly one file in field slide.')
            upload = files[0]
            if not (upload.filename or '').lower().endswith('.svs'):
                raise HTTPException(400, 'Choose a .svs slide file.')
            sha, md5, size = hashlib.sha256(), hashlib.md5(), 0
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_FILE_BYTES:
                    raise HTTPException(413, 'Upload too large. The demo limit is 80 MB per slide.')
                sha.update(chunk)
                md5.update(chunk)
            if size == 0:
                raise HTTPException(400, 'The uploaded slide is empty. Choose the supplied slide file.')
            # Filename, optional case_id, specimen label and diagnosis never enter the classifier.
            return api.state.jobs.submit((sha.hexdigest(), size, md5.hexdigest()))

    @api.get('/jobs/{key}')
    def get_job(key: str):
        return api.state.jobs.get(key)

    @api.delete('/jobs/{key}')
    def cancel_job(key: str):
        return api.state.jobs.cancel(key)

    @api.get('/jobs/{key}/overlay')
    def overlay(key: str):
        if api.state.jobs.get(key)['status'] != 'done':
            raise HTTPException(404, 'No analyzed tile overlay is available for this job.')
        return FileResponse(api.state.jobs.output / 'analyzed_tiles_overlay.jpg', media_type='image/jpeg')

    return BoundedUpload(api)


app = create_app()
