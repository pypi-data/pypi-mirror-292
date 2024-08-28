import jax
import jax.numpy as jnp
import numpy as np
import optax
from einops import reduce
from flax import nnx

from jimmy.models import DINOV2_VITS14, load_model
from jimmy.models.mamba import MambaVision, VMamba2
from jimmy.models.mlla import Mlla

# from jimmy.models.mlla import Mlla
from datetime import datetime
from jimmy.layers.mamba import Mamba2VisionMixer, MambaVisionMixer, Mamba2Mixer
from jimmy.models.emamodel import EmaModel
from jimmy.models.fastervit import FasterViT

# Initialize random number generator
rngs = nnx.Rngs(42)


# # Load the model
# class Model(nnx.Module):
#     def __init__(self, rngs):
#         self.backbone = load_model(
#             DINOV2_VITS14,
#             rngs=rngs,
#             pretrained=False,
#         )
#         self.fc = nnx.Linear(384, 1, rngs=rngs)

#     def __call__(self, x):
#         x = self.backbone(x)
#         x = reduce(x, "b n c -> b c", "mean")
#         x = self.fc(x)
#         return x


# model = Model(rngs)
# ema_model = EmaModel(model)
# model.train()
# ema_model.model.eval()
# model = MambaVision(
#     in_features=3,
#     dim=64,
#     in_dim=32,
#     depths=[1, 3, 8, 4],
#     num_heads=[2, 4, 8, 16],
#     layer_window_sizes=[-1, -1, -1, -1],  # [8, 8, 14, 7],
#     msa_window_sizes=[8, 8, 14, 7],  # [8, 8, 14, 7],
#     # msa_window_sizes=[-1, -1, -1, -1],  # [8, 8, 14, 7],
#     drop_path_rate=0.2,
#     num_classes=1,
#     # mamba_mixer=Mamba2Mixer,
#     rngs=rngs,
# )
# model = Mlla(
#     num_classes=1,
#     # depths=[2,4,12,4],
#     depths=[1, 3, 8, 4],
#     patch_size=4,
#     in_features=3,
#     embed_dim=96,  # 64 for VMamba2
#     num_heads=[2, 4, 8, 16],
#     layer_window_sizes=[-1, -1, -1, -1],
#     rngs=rngs,
# )
# model = FasterViT(
#     in_features=3,
#     dim=64,
#     in_dim=64,
#     resolution=224,
#     depths=[2, 3, 6, 5],
#     hat=[False, False, True, False],
#     num_heads=[2, 4, 8, 16],
#     window_sizes=[7, 7, 7, 7],
#     ct_size=2,
#     rngs=rngs,
# )
ema_model = EmaModel(model)
model.train()
ema_model.model.eval()


b1 = 0.95
retuned_lr = 1e-3
learning_rate_fn = optax.schedules.warmup_constant_schedule(
    init_value=0.0, peak_value=retuned_lr, warmup_steps=2
)
optimizer = optax.adam(learning_rate_fn, b1=0.0)
optimizer = optax.contrib.schedule_free(optimizer, learning_rate_fn, b1=b1)

optimizer = nnx.Optimizer(model, optimizer)  # reference sharing


@nnx.jit
def train(model, ema_model, emaf, optimizer, x, y):
    def loss_fn(model, ema_model):
        y_pred = model(x)

        loss = ((y_pred - y) ** 2).mean()

        ema_y_pred = ema_model(x)
        loss += emaf * ((y_pred - ema_y_pred) ** 2).mean()

        return loss

    loss, grads = nnx.value_and_grad(loss_fn)(model, ema_model)

    optimizer.update(grads)
    params = nnx.state(model, nnx.Param)

    ema_model.update(params)

    return loss


# arr = np.random.randn(2, 224, 224, 3)
arr = np.random.randn(2, 224, 224, 3)
x = jnp.array(arr)
y = jnp.array([[0.0], [1.0]])

t0 = datetime.now()
for i in range(16):
    loss = train(model, ema_model, 0.3 if i > 8 else 0, optimizer, x, y)
    print(i, loss)
t1 = datetime.now()

print(t1 - t0)
