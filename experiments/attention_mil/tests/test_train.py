import json
from pathlib import Path

import pytest
import torch
import torch.nn.functional as F

from experiments.attention_mil import train as train_module
from experiments.attention_mil.data import Normalizer, load_split, training_file_ids
from experiments.attention_mil.train import class_weights, select_seed, train_one_seed

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'frozen_config.json'
CONFIG = json.loads(CONFIG_PATH.read_text())


def test_class_weights_favour_the_smaller_class(bundle):
    w = class_weights(load_split(bundle, 'train'))   # 11 / 11 / 10 slides
    assert torch.allclose(w, torch.tensor([32 / 33, 32 / 33, 32 / 30]))


def test_builtin_class_weight_cancels_with_one_slide_per_step():
    """Why train.py multiplies the weight by hand."""
    logits, target, weight = torch.tensor([[2.0, 0.5, -1.0]]), torch.tensor([2]), torch.tensor([1.0, 1.0, 3.0])
    plain = F.cross_entropy(logits, target)
    assert torch.isclose(F.cross_entropy(logits, target, weight=weight), plain)    # weight lost
    assert torch.isclose(plain * weight[2], 3 * plain)                            # what train.py does


def test_seed_selection_rule_and_tie_breaks():
    s = lambda seed, f1, loss: {'seed': seed, 'validation_macro_f1': f1, 'validation_loss': loss}
    assert select_seed([s(215, 0.6, 0.5), s(216, 0.8, 0.9)]) == 216          # higher F1 wins
    assert select_seed([s(215, 0.8, 0.7), s(216, 0.8, 0.4)]) == 216          # F1 tie: lower loss
    assert select_seed([s(217, 0.8, 0.4), s(216, 0.8, 0.4)]) == 216          # full tie: lower seed


def test_same_seed_trains_identically(bundle):
    train = load_split(bundle, 'train')[:6]
    validation = load_split(bundle, 'validation')
    norm = Normalizer.fit(load_split(bundle, 'train'), training_file_ids(bundle))
    quiet = lambda *_: None
    a = train_one_seed(CONFIG, 215, train, validation, norm, max_epochs=2, log=quiet)
    b = train_one_seed(CONFIG, 215, train, validation, norm, max_epochs=2, log=quiet)
    assert a['history'] == b['history']
    for key in a['best']['state']:
        assert torch.equal(a['best']['state'][key], b['best']['state'][key])


def test_full_run_never_requests_test_slides_and_refuses_overwrite(bundle, tmp_path, monkeypatch):
    requested = []
    real = train_module.load_split

    def recording(bundle_path, split_name, **kwargs):
        requested.append(split_name)
        return real(bundle_path, split_name, **kwargs)

    monkeypatch.setattr(train_module, 'load_split', recording)
    out = tmp_path / 'run'
    args = ['--bundle', str(bundle), '--config', str(CONFIG_PATH), '--out', str(out), '--max-epochs', '1']
    report = train_module.main(args)
    assert set(requested) == {'train', 'validation'}
    assert len(report['seeds']) == 5 and (out / 'seed_215/model.pt').is_file()
    with pytest.raises(SystemExit, match='refusing to overwrite'):
        train_module.main(args)
