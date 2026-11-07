import pytest
import torch

from experiments.attention_mil.model import GatedAttentionMIL, build_model, count_parameters

CONFIG = {'hidden': 256, 'attention': 128, 'dropout': 0.25}


def tiles(n, seed=0):
    return torch.randn(n, 1536, generator=torch.Generator().manual_seed(seed))


@pytest.mark.parametrize('n', [1, 467, 512])
def test_outputs_have_right_shape_and_alpha_is_a_distribution(n):
    model = build_model(CONFIG, seed=215).eval()
    logits, alpha = model(tiles(n))
    assert logits.shape == (3,) and alpha.shape == (n,)
    assert torch.all(alpha >= 0) and torch.isclose(alpha.sum(), torch.tensor(1.0))


@pytest.mark.parametrize('shape', [(0, 1536), (10, 1535), (2, 10, 1536)])
def test_rejects_malformed_input(shape):
    with pytest.raises(ValueError):
        GatedAttentionMIL()(torch.zeros(shape))


def test_parameter_count():
    assert count_parameters(GatedAttentionMIL()) == 460_163


def test_tile_order_does_not_matter():
    """A slide is a set of tiles: shuffling them must not change the prediction."""
    model = build_model(CONFIG, seed=215).eval()
    x = tiles(100)
    order = torch.randperm(100, generator=torch.Generator().manual_seed(1))
    logits, alpha = model(x)
    logits2, alpha2 = model(x[order])
    assert torch.allclose(logits, logits2, atol=1e-5)
    assert torch.allclose(alpha[order], alpha2)


def test_equal_scores_reduce_to_mean_pooling():
    """With all attention scores equal, alpha = 1/n: the existing model's plain mean."""
    model = build_model(CONFIG, seed=215).eval()
    with torch.no_grad():
        model.attention_w.weight.zero_()
        x = tiles(64)
        _, alpha = model(x)
        assert torch.allclose(alpha, torch.full((64,), 1 / 64))
        h = model.embed(x)
        assert torch.allclose(alpha @ h, h.mean(dim=0), atol=1e-6)


def test_same_seed_gives_identical_model_different_seed_does_not():
    a, b, c = build_model(CONFIG, 215), build_model(CONFIG, 215), build_model(CONFIG, 216)
    for pa, pb in zip(a.parameters(), b.parameters()):
        assert torch.equal(pa, pb)
    assert not torch.equal(a.embed[0].weight, c.embed[0].weight)


def test_dropout_only_active_in_training_mode():
    model = build_model(CONFIG, seed=215)
    x = tiles(50)
    model.eval()
    assert torch.equal(model(x)[0], model(x)[0])
    model.train()
    assert not torch.equal(model(x)[0], model(x)[0])


def test_gradients_reach_every_parameter():
    model = build_model(CONFIG, seed=215).train()
    logits, _ = model(tiles(20))
    torch.nn.functional.cross_entropy(logits[None], torch.tensor([2])).backward()
    for name, p in model.named_parameters():
        assert p.grad is not None and p.grad.abs().sum() > 0, name


def test_learns_to_attend_to_the_few_informative_tiles():
    """Synthetic bags: 47 noise tiles + 3 'marker' tiles whose direction encodes the class.

    Mean pooling dilutes 3 markers among 50 tiles; attention should find them.
    """
    g = torch.Generator().manual_seed(0)
    markers = torch.randn(3, 1536, generator=g) * 3

    def bag(label):
        x = torch.randn(50, 1536, generator=g)
        x[:3] += markers[label]
        return x, label

    torch.manual_seed(0)
    model = GatedAttentionMIL(dropout=0.0)
    optimiser = torch.optim.Adam(model.parameters(), lr=1e-3)
    for step in range(150):
        x, y = bag(step % 3)
        logits, _ = model(x)
        loss = torch.nn.functional.cross_entropy(logits[None], torch.tensor([y]))
        optimiser.zero_grad(); loss.backward(); optimiser.step()

    model.eval()
    correct, marker_weight = 0, []
    with torch.no_grad():
        for i in range(30):
            x, y = bag(i % 3)
            logits, alpha = model(x)
            correct += int(logits.argmax() == y)
            marker_weight.append(alpha[:3].sum().item())
    assert correct == 30
    # Uniform attention would give the 3 markers 3/50 = 0.06 of the weight.
    # Observed on 2026-11-06: min 0.34, mean 0.55, and no higher with 4x more steps:
    # once the bag is classified correctly the loss stops pushing attention to sharpen.
    uniform = 3 / 50
    assert min(marker_weight) > 5 * uniform


def test_untrained_model_runs_on_a_real_normalised_slide(bundle):
    from experiments.attention_mil.data import Normalizer, load_split, training_file_ids
    train = load_split(bundle, 'train')
    norm = Normalizer.fit(train, training_file_ids(bundle))
    slide = load_split(bundle, 'validation')[0]
    logits, alpha = build_model(CONFIG, 215).eval()(torch.from_numpy(norm.transform(slide.features)))
    assert torch.isfinite(logits).all() and alpha.shape == (len(slide.features),)
    assert torch.isclose(alpha.sum(), torch.tensor(1.0))
