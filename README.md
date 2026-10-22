---
title: Gemma 3 12B IT
emoji: 💎
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.30.0
app_file: app.py
pinned: false
license: gemma
models:
  - google/gemma-3-12b-it
short_description: Multimodal chat demo for google/gemma-3-12b-it
---

# Gemma 3 12B IT: chat demo

A Gradio chat demo for [google/gemma-3-12b-it](https://huggingface.co/google/gemma-3-12b-it).
It takes text and images, streams its answers, and runs on ZeroGPU.

## Deploy

1. Create a new Space (SDK: **Gradio**, hardware: **ZeroGPU**) and push these files to it.
2. Gemma is a **gated model**. Accept the licence on the model page with your HF account.
3. In the Space settings, add a secret named `HF_TOKEN` holding a read token from that account.

`MODEL_ID` can be overridden with a Space variable, for example `google/gemma-3-4b-it` for a smaller model.

## Run locally

Needs a GPU with about 24 GB of VRAM (bf16).

```bash
pip install gradio -r requirements.txt
huggingface-cli login
python app.py
```
