import jax
import jax.numpy as jnp
import numpy as np
import optax
from einops import reduce
from flax import nnx
from jimmy.models import DINOV2_VITS14, load_model
from jimmy.models.mamba import MambaVision
from jimmy.layers.mamba import window_partition, Mamba2VisionMixer

# Initialize random number generator
rngs = nnx.Rngs(42)

# model = Model(rngs)
model = MambaVision(
    in_features=3,
    depths=[1, 3, 8, 4],
    num_heads=[2, 4, 8, 16],
    window_size=[8, 8, 14, 7],
    dim=64,  # 80
    in_dim=32,
    mlp_ratio=4,
    drop_path_rate=0.2,
    num_classes=1,
    mamba_mixer=Mamba2VisionMixer,
    rngs=rngs,
)


arr = np.random.randn(1, 518, 518, 3)
x = jnp.array(arr)
y = jnp.array([[0.0], [1.0]])

model(x)

H = W = 518

embedded = model.patch_embed(x)
pad_r = (8 - W % 8) % 8
pad_b = (8 - H % 8) % 8
if pad_r > 0 or pad_b > 0:
    embedded = jnp.pad(x, ((0, 0), (0, pad_b), (0, pad_r), (0, 0)))
    _, Hp, Wp, _ = x.shape
else:
    Hp, Wp = H, W

d_model = 64
arr = np.random.randn(289, 64, d_model)
x = jnp.array(arr)

# embedded = window_partition(embedded, 8)
mixer = Mamba2VisionMixer(d_model, rngs=rngs)
self = mixer
