"""Guards for the official run. None of these tests opens the test split."""
import json
from pathlib import Path

import pytest

from experiments.attention_mil import evaluate, train
from experiments.attention_mil.compare_runs import compare

CONFIG = Path(__file__).resolve().parents[1] / 'frozen_config.json'


@pytest.fixture(scope='module')
def runs(bundle, tmp_path_factory):
    root = tmp_path_factory.mktemp('runs')
    base = ['--bundle', str(bundle), '--config', str(CONFIG), '--max-epochs', '1']
    train.main(base + ['--out', str(root / 'native')])
    train.main(base + ['--out', str(root / 'official'), '--authoritative'])
    return root / 'native', root / 'official'


def test_authoritative_run_records_chosen_seed_and_sources(runs):
    native, official = runs
    assert 'native_preferred_seed' in json.loads((native / 'seed_search.json').read_text())
    search = json.loads((official / 'seed_search.json').read_text())
    run = json.loads((official / 'run.json').read_text())
    assert search['chosen_seed'] in range(215, 220) and run['authoritative'] is True
    assert set(run['source_sha256']) >= {'data.py', 'model.py', 'train.py', 'evaluate.py'}


def test_test_evaluation_refuses_a_native_run(bundle, runs):
    with pytest.raises(SystemExit, match='no chosen_seed'):
        evaluate.main(['--bundle', str(bundle), '--run', str(runs[0])])


def test_test_evaluation_refuses_a_changed_model_file(bundle, runs, tmp_path):
    import shutil
    copy = tmp_path / 'official'
    shutil.copytree(runs[1], copy)
    seed = json.loads((copy / 'seed_search.json').read_text())['chosen_seed']
    with open(copy / f'seed_{seed}/model.pt', 'ab') as f:
        f.write(b'tampered')
    with pytest.raises(SystemExit, match='changed since training'):
        evaluate.main(['--bundle', str(bundle), '--run', str(copy)])


def test_test_evaluation_refuses_to_repeat(bundle, runs, tmp_path):
    import shutil
    copy = tmp_path / 'official'
    shutil.copytree(runs[1], copy)
    (copy / 'test.json').write_text('{}')
    with pytest.raises(SystemExit, match='refusing to repeat'):
        evaluate.main(['--bundle', str(bundle), '--run', str(copy)])


def test_identical_runs_compare_as_identical(runs):
    native, official = runs
    result = compare(native, official)    # same machine, same seeds: must match exactly
    assert result['same_seed_selected']
    assert result['max_abs_alpha_diff_all_seeds'] == 0 and result['normalization_max_abs_diff'] == 0
