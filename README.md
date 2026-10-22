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
short_description: Multimodal chat demo for Gemma 3 12B on Vertex AI
---

# Gemma 3 12B IT: chat demo (Vertex AI backend)

A Gradio chat demo for [google/gemma-3-12b-it](https://huggingface.co/google/gemma-3-12b-it).
It takes text and images. The Space runs on free CPU hardware; the model itself runs on a
Vertex AI endpoint in your Google Cloud project.

## 1. Deploy Gemma 3 12B on Vertex AI

In the Google Cloud console: **Vertex AI → Model Garden → Gemma 3 → Deploy**, pick the
`gemma-3-12b-it` variant with the vLLM serving container, and note the **endpoint ID** and **region**.

> The endpoint bills for as long as it is deployed, even with no traffic. Undeploy it when you are done.

## 2. Create a service account

Give it the **Vertex AI User** role (`roles/aiplatform.user`) and create a JSON key.

## 3. Configure the Space

| Name | Kind | Value |
|---|---|---|
| `GCP_SA_KEY` | Secret | Full contents of the service-account JSON key |
| `GCP_PROJECT` | Variable | Your Google Cloud project ID |
| `GCP_REGION` | Variable | Endpoint region (default `us-central1`) |
| `VERTEX_ENDPOINT_ID` | Variable | Numeric endpoint ID |
| `VERTEX_DEDICATED_ENDPOINT` | Variable | `true` (Model Garden default) or `false` for a shared endpoint |

Hardware: **CPU basic** is enough.

## Run locally

```bash
pip install gradio -r requirements.txt
gcloud auth application-default login   # or export GCP_SA_KEY
GCP_PROJECT=... VERTEX_ENDPOINT_ID=... python app.py
```
