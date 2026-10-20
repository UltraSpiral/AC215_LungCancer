"""Replay the bounded MS2 workflow with existing real inputs and saved features.

The new 16-tile preprocessing smoke is separate from the immutable 512-tile
model cache. No UNI2 extraction, training, download or metric evaluation runs.
"""
from pathlib import Path
import argparse
import http.client
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lungcancer.common import atomic_json, checksum, utcnow


def command(args, output, env):
    """Retain combined output and fail on the actual command exit status."""
    print('Running: ' + ' '.join(args), flush=True)
    with output.open('w') as log:
        log.write(json.dumps({'argv': args}) + '\n')
        with subprocess.Popen(args, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True) as process:
            for line in process.stdout:
                log.write(line)
                print(line, end='', flush=True)
            status = process.wait()
    if status:
        raise RuntimeError(f'Command exited {status}; inspect {output.name}')


def get(port, path):
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=30)
    try:
        conn.request('GET', path)
        response = conn.getresponse()
        data = response.read(4 * 1024 * 1024 + 1)
        if response.status != 200 or len(data) > 4 * 1024 * 1024:
            raise RuntimeError(f'GET {path} failed: HTTP {response.status}')
        return data
    finally:
        conn.close()


def upload(port, source):
    boundary = 'lungcancer-' + uuid.uuid4().hex
    prefix = (f'--{boundary}\r\nContent-Disposition: form-data; name="slide"; '
              'filename="sample.svs"\r\nContent-Type: application/octet-stream\r\n\r\n').encode()
    suffix = f'\r\n--{boundary}--\r\n'.encode()
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=60)
    try:
        conn.putrequest('POST', '/api/jobs')
        conn.putheader('Content-Type', 'multipart/form-data; boundary=' + boundary)
        conn.putheader('Content-Length', str(len(prefix) + source.stat().st_size + len(suffix)))
        conn.endheaders()
        conn.send(prefix)
        with source.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                conn.send(chunk)
        conn.send(suffix)
        response = conn.getresponse()
        data = response.read(65537)
        if response.status != 202 or len(data) > 65536:
            raise RuntimeError(f'Upload failed: HTTP {response.status}')
        result = json.loads(data)
        if not re.fullmatch(r'[a-f0-9]{32}', result['job_id']):
            raise ValueError('Unexpected job identifier')
        return result
    finally:
        conn.close()


def image_identity(name, env):
    data = json.loads(subprocess.check_output(
        ['docker', 'image', 'inspect', name], cwd=ROOT, env=env, text=True))[0]
    if data['Architecture'] != 'arm64' or data['Os'] != 'linux':
        raise ValueError('Expected a native Linux ARM64 image')
    return {'id': data['Id'], 'os': data['Os'], 'architecture': data['Architecture']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if platform.machine().lower() not in {'arm64', 'aarch64'}:
        raise ValueError('This demonstrated workflow requires native ARM64')
    env = dict(os.environ)
    bundle = (args.bundle or Path(env.get('LC_APP_BUNDLE', env.get(
        'LC_CPU_BUNDLE', str(ROOT / 'local_data/cpu_bundle'))))).resolve()
    if not (bundle / 'manifest.json').is_file():
        raise ValueError('Existing private bundle missing; do not download replacement inputs')
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-' + uuid.uuid4().hex[:8]
    output = (args.output or ROOT / 'local_outputs/ms2' / stamp).resolve()
    if not output.is_relative_to((ROOT / 'local_outputs').resolve()):
        raise ValueError('Keep demo outputs inside ignored local_outputs/')
    output.mkdir(parents=True, exist_ok=False)
    prep_output = output / 'preprocessing'
    prep_output.mkdir()
    for key in ('LC_CPU_BUNDLE', 'LC_APP_BUNDLE'):
        env[key] = str(bundle)
    env.update(LC_CPU_OUTPUT=str(prep_output), LC_CPU_PLATFORM='linux/arm64',
               LC_CPU_UID=str(os.getuid()), LC_CPU_GID=str(os.getgid()))
    report = {'status': 'running', 'started_at': utcnow(), 'stages': {},
              'scope': 'Versioned prepared inputs, real preprocessing smoke and cached-feature HTTP inference',
              'new_preprocessing_smoke_tiles_are_model_inputs': False,
              'uni2_encoding_performed': False, 'training_performed': False,
              'new_test_metric_evaluation_performed': False,
              'full_fresh_uni2_container_verification': 'pending',
              'runner_sha256': checksum(Path(__file__)),
              'source_git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_working_tree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT))}
    try:
        manifest = json.loads((bundle / 'manifest.json').read_text())
        model = json.loads((bundle / 'run/model/model.json').read_text())
        source = (bundle / manifest['real_slide']['path']).resolve()
        if not source.is_relative_to(bundle) or not source.is_file():
            raise ValueError('Unsafe or missing supplied slide')
        report['input'] = {'file_id': manifest['real_slide']['file_id'],
                           'source_bytes': source.stat().st_size, 'source_sha256': checksum(source),
                           'manifest_sha256': checksum(bundle / 'manifest.json'),
                           'data_snapshot_identifier': manifest['data_snapshot_identifier'],
                           'model_identifier': model['model_identifier']}
        atomic_json(output / 'demo.json', report)
        command(['make', 'app-up'], output / 'app-start.txt', env)
        port = int(env.get('LC_APP_PORT', '8080'))
        if not 1 <= port <= 65535:
            raise ValueError('Invalid application port')
        health = json.loads(get(port, '/api/health'))
        if (health['status'] != 'ready' or health['processing_mode'] != 'preprocessed_slide_demo'
                or health['uni2_encoding_performed'] is not False):
            raise ValueError('Unexpected API mode')
        report['stages']['app'] = health
        command(['make', 'cpu-build'], output / 'cpu-build.txt', env)
        command(['docker', 'compose', '-f', 'compose.cpu.yml', 'run', '--rm', 'real-preprocess'],
                output / 'preprocess.txt', env)
        prep = json.loads((prep_output / 'verification_preprocess.json').read_text())
        if prep['status'] != 'success' or prep['data_snapshot_identifier'] != manifest['data_snapshot_identifier']:
            raise ValueError('Preprocessing/input snapshot verification failed')
        report['stages']['preprocessing'] = prep
        submission = upload(port, source)
        atomic_json(output / 'job-submitted.json', submission)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            job = json.loads(get(port, '/api/jobs/' + submission['job_id']))
            if job['status'] in {'done', 'failed'}:
                break
            time.sleep(0.25)
        else:
            raise TimeoutError('Timed out waiting for the real prediction')
        atomic_json(output / 'prediction.json', job)
        if job['status'] != 'done' or job['result']['status'] != 'success':
            raise ValueError('Real prediction failed; inspect prediction.json')
        result = job['result']
        probabilities = result['class_probabilities']
        if (set(probabilities) != set(model['classes'])
                or not all(math.isfinite(p) and 0 <= p <= 1 for p in probabilities.values())
                or abs(sum(probabilities.values()) - 1) > 1e-6):
            raise ValueError('Invalid named probabilities')
        if (result['model_identifier'] != model['model_identifier']
                or result['data_snapshot_identifier'] != manifest['data_snapshot_identifier']
                or result['source_sha256'] != report['input']['source_sha256']
                or result['uni2_encoding_performed'] is not False):
            raise ValueError('Result provenance mismatch')
        references = []
        for split in ('validation', 'test'):
            references += json.loads((bundle / f'run/evaluation_{split}/predictions.json').read_text())
        reference = next(row for row in references if row['file_id'] == report['input']['file_id'])
        delta = max(abs(result['class_probabilities'][c] - reference['class_probabilities'][c])
                    for c in model['classes'])
        if delta > 1e-8:
            raise ValueError('Result differs from the frozen prediction reference')
        overlay_path = '/api/jobs/' + submission['job_id'] + '/overlay'
        if result['analyzed_tiles_overlay'] != overlay_path:
            raise ValueError('Unexpected overlay URL')
        overlay = get(port, overlay_path)
        if not overlay.startswith(b'\xff\xd8'):
            raise ValueError('Expected actual JPEG overlay')
        (output / 'analyzed_tiles_overlay.jpg').write_bytes(overlay)
        report['stages']['prediction'] = {'status': 'success', 'result': result,
                                          'maximum_frozen_reference_difference': delta}
        report['images'] = {}
        for service in ('api', 'web'):
            container = subprocess.check_output(
                ['docker', 'compose', '-f', 'compose.app.yml', 'ps', '-q', service],
                cwd=ROOT, env=env, text=True).strip()
            image_id = subprocess.check_output(['docker', 'inspect', '--format', '{{.Image}}', container],
                                               env=env, text=True).strip()
            report['images'][service] = image_identity(image_id, env)
        report['images']['preprocessing'] = image_identity(
            env.get('LC_CPU_IMAGE') or 'lungcancer-cpu:milestone2', env)
        report['status'] = 'success'
    except Exception as exc:
        report.update(status='error', reason=str(exc))
        raise
    finally:
        report['finished_at'] = utcnow()
        atomic_json(output / 'demo.json', report)
        print(f'MS2 demo {report["status"]}; evidence: {output}', flush=True)


if __name__ == '__main__':
    main()
