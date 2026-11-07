import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture(scope='session')
def bundle():
    """Real cached bundle: local_data/cpu_bundle natively, /inputs in Docker (ATTN_BUNDLE)."""
    path = Path(os.environ.get('ATTN_BUNDLE', REPO / 'local_data/cpu_bundle'))
    if not (path / 'run/model/model.json').is_file():
        pytest.skip(f'cached bundle not available at {path}')
    return path
