"""Phase 2: gated attention MIL head (Ilse, Tomczak & Welling, ICML 2018).

A slide is a "bag" of tiles. Each tile is already a 1536-number UNI2-h vector.
The model scores how much each tile should count, takes a weighted average of
the tiles with those weights, and classifies the average:

    h_i  = Dropout(ReLU(W_in x_i))                 tile vector -> 256 numbers
    a_i  = w . ( tanh(V h_i) * sigmoid(U h_i) )     one raw score per tile
    alpha = softmax(a)  over the tiles of the slide  weights >= 0, sum to 1
    z    = sum_i alpha_i h_i                         slide vector (weighted average)
    logits = W_out Dropout(z)                        3 class scores

The existing model is the special case alpha_i = 1/n for every tile (a plain
mean). Here alpha is learned, and alpha is what the heatmap paints.
"""
import torch
from torch import nn

INPUT_DIM = 1536
N_CLASSES = 3


class GatedAttentionMIL(nn.Module):
    def __init__(self, hidden=256, attention=128, dropout=0.25, n_classes=N_CLASSES):
        super().__init__()
        # 1536 -> 256: compress each tile and let training choose what matters.
        self.embed = nn.Sequential(nn.Linear(INPUT_DIM, hidden), nn.ReLU(), nn.Dropout(dropout))
        # Gated attention: tanh branch says "what", sigmoid branch is a 0..1 gate.
        self.attention_v = nn.Linear(hidden, attention)
        self.attention_u = nn.Linear(hidden, attention)
        # Bias would add the same constant to every tile's score; softmax ignores it.
        self.attention_w = nn.Linear(attention, 1, bias=False)
        self.classifier = nn.Sequential(nn.Dropout(dropout), nn.Linear(hidden, n_classes))

    def forward(self, tiles):
        """tiles: [n_tiles, 1536] for ONE slide. Returns (logits [3], alpha [n_tiles])."""
        if tiles.ndim != 2 or tiles.shape[1] != INPUT_DIM or len(tiles) == 0:
            raise ValueError(f'expected [n_tiles>0, {INPUT_DIM}], got {tuple(tiles.shape)}')
        h = self.embed(tiles)                                            # [n, 256]
        gate = torch.tanh(self.attention_v(h)) * torch.sigmoid(self.attention_u(h))
        scores = self.attention_w(gate).squeeze(1)                       # [n]
        alpha = torch.softmax(scores, dim=0)                             # [n], sums to 1
        z = alpha @ h                                                    # [256]
        return self.classifier(z), alpha


def build_model(config, seed):
    """Same seed + same config -> identical starting weights."""
    torch.manual_seed(seed)
    return GatedAttentionMIL(hidden=config['hidden'], attention=config['attention'],
                             dropout=config['dropout'])


def count_parameters(model):
    return sum(p.numel() for p in model.parameters())
