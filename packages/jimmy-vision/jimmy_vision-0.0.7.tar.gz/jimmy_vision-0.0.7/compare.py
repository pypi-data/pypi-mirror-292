import jax.numpy as jnp
import numpy as np
import torch
from flax import nnx

from jimmy.models.mamba import MambaVision
from tests.torchimpl import MambaVisionTorch, mamba_vision_T

torch_model = mamba_vision_T()

rngs = nnx.Rngs(0)
jax_model = MambaVision(
    in_features=3,
    dim=80,
    in_dim=32,
    depths=[1, 3, 8, 4],
    window_size=[8, 8, 14, 7],
    mlp_ratio=4,
    num_heads=[2, 4, 8, 16],
    drop_path_rate=0.2,
    rngs=rngs,
)

arr = np.random.normal(1, size=(1, 3, 224, 224))

jax_arr = jnp.asarray(arr).transpose(0, 2, 3, 1)
torch_arr = torch.tensor(arr).float()

a = torch_model(torch_arr)
b = jax_model(jax_arr)
