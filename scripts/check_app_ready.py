"""Check the actual browser-facing route after Compose health checks pass."""
from pathlib import Path
import json
import os
import time
import urllib.error
import urllib.request


def main():
    port = int(os.environ.get('LC_APP_PORT', '8080'))
    if not 1 <= port <= 65535:
        raise ValueError('LC_APP_PORT must be a valid TCP port')
    url = f'http://127.0.0.1:{port}/api/health'
    for attempt in range(20):
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                result = json.load(response)
            if (result['status'] != 'ready' or result['processing_mode'] != 'preprocessed_slide_demo'
                    or result['uni2_encoding_performed'] is not False):
                raise ValueError('Unexpected application health response')
            root = Path(__file__).resolve().parents[1]
            output = root / 'local_outputs/app/readiness.json'
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps({'url': url, **result}, indent=2) + '\n')
            print(f'App ready: http://127.0.0.1:{port}/ (real backend verified)')
            return
        except (urllib.error.URLError, TimeoutError):
            if attempt == 19:
                raise RuntimeError('The app browser route is unreachable; inspect make app-logs.') from None
            time.sleep(1)


if __name__ == '__main__':
    main()
