---
title: Wan2.1 Video Demo (WanGP)
emoji: 🎬
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
suggested_hardware: l4x1
pinned: false
license: apache-2.0
short_description: Text-to-video with DeepBeepMeep/Wan2.1 weights via WanGP
models:
  - DeepBeepMeep/Wan2.1
---

# Wan2.1 Video Demo

Gradio demo for the [DeepBeepMeep/Wan2.1](https://huggingface.co/DeepBeepMeep/Wan2.1) checkpoints.

Those weights are packaged for **[WanGP](https://github.com/deepbeepmeep/Wan2GP)** (DeepBeepMeep's
low‑VRAM Wan runtime, `mmgp` offloading + quanto int8), not for `diffusers`. This Space therefore
installs WanGP at a pinned commit and drives it through its in‑process Python API
(`shared/api.py`). WanGP downloads the required files from `DeepBeepMeep/Wan2.1` on first use.

**This demo uses WanGP** — see its terms in the WanGP repository.

## Models

| Choice | WanGP `model_type` | Default | VRAM (approx.) |
|---|---|---|---|
| Wan2.1 Text2Video 1.3B | `t2v_1.3B` | ✅ | fits on a 24 GB L4 |
| Wan2.1 Text2Video 14B | `t2v` | set `ENABLE_14B=1` | needs ≥ 40 GB RAM, L40S/A100 recommended |
| Wan2.1 Image2Video 480p 14B | `i2v` | set `ENABLE_14B=1` | same as above |

## Output modes

- **Video**: MP4 at 16 fps.
- **Image**: WanGP's Wan2.1 T2V has no native image output, so the demo renders a short
  17-frame clip and returns its middle frame as a PNG.

## Hardware

- Requires a GPU Space (Docker SDK). ZeroGPU is **not** supported: WanGP keeps the model
  resident in a long‑lived process, which conflicts with ZeroGPU's per‑call GPU allocation.
- Recommended: `Nvidia L4` for 1.3B; `L40S` or `A100` for 14B.
- Optional: attach persistent storage (mounted at `/data`) so checkpoints survive restarts.

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `ENABLE_14B` | `0` | Expose the 14B T2V/I2V models |
| `WANGP_PROFILE` | `4` | WanGP memory profile (see WanGP docs) |
| `WANGP_ATTENTION` | `sdpa` | Attention backend |
| `MAX_FRAMES` | `81` | Upper bound of the frame slider |
