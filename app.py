"""Gradio demo for google/gemma-3-12b-it (text + image chat), served from a Vertex AI endpoint."""

import base64
import json
import mimetypes
import os

import gradio as gr
from google.cloud import aiplatform
from google.oauth2 import service_account

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
MAX_IMAGES = 5

PROJECT = os.environ["GCP_PROJECT"]
REGION = os.getenv("GCP_REGION", "us-central1")
ENDPOINT_ID = os.environ["VERTEX_ENDPOINT_ID"]
# Model Garden deployments default to a dedicated endpoint; set to "false" for a shared one.
DEDICATED_ENDPOINT = os.getenv("VERTEX_DEDICATED_ENDPOINT", "true").lower() == "true"

# Service-account key JSON stored as a Space secret; falls back to Application Default Credentials.
credentials = None
if os.getenv("GCP_SA_KEY"):
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GCP_SA_KEY"]),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

aiplatform.init(project=PROJECT, location=REGION, credentials=credentials)
endpoint = aiplatform.Endpoint(ENDPOINT_ID)


def _is_image(path: str) -> bool:
    return path.lower().endswith(IMAGE_EXTENSIONS)


def _image_part(path: str) -> dict:
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}}


def _to_parts(content) -> list[dict]:
    """Convert any Gradio chat content shape into OpenAI-style chat parts."""
    if content is None:
        return []
    if isinstance(content, str):
        return [{"type": "text", "text": content}] if content.strip() else []
    if isinstance(content, (list, tuple)):
        return [part for item in content for part in _to_parts(item)]
    if isinstance(content, dict):
        if content.get("type") == "text":
            return _to_parts(content.get("text", ""))
        if content.get("type") == "file":
            return _to_parts(content.get("file"))
        path = content.get("path")
        return [_image_part(path)] if path and _is_image(path) else []
    path = getattr(content, "path", None)  # gr.FileData
    return [_image_part(path)] if path and _is_image(path) else []


def build_messages(message: dict, history: list[dict], system_prompt: str) -> list[dict]:
    messages = []
    if system_prompt.strip():
        messages.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})

    for turn in history:
        parts = _to_parts(turn.get("content"))
        if not parts:
            continue
        # Merge consecutive turns from the same role (Gradio splits text and files).
        if messages and messages[-1]["role"] == turn["role"]:
            messages[-1]["content"].extend(parts)
        else:
            messages.append({"role": turn["role"], "content": parts})

    files = [f if isinstance(f, dict) else {"path": f} for f in message.get("files", [])]
    user_parts = _to_parts(files) + _to_parts(message.get("text", ""))
    if messages and messages[-1]["role"] == "user":
        messages[-1]["content"].extend(user_parts)
    else:
        messages.append({"role": "user", "content": user_parts})
    return messages


def _extract_text(predictions) -> str:
    """Read the reply from a vLLM chat-completions prediction (dict, or list of dicts/strings)."""
    if isinstance(predictions, list):
        predictions = predictions[0] if predictions else ""
    if isinstance(predictions, dict) and "choices" in predictions:
        return predictions["choices"][0]["message"]["content"]
    if isinstance(predictions, str):
        return predictions.split("Output:", 1)[-1].strip()
    raise gr.Error(f"Unexpected response from the endpoint: {str(predictions)[:300]}")


def generate(message: dict, history: list[dict], system_prompt: str, max_new_tokens: int, temperature: float):
    messages = build_messages(message, history, system_prompt)

    n_images = sum(p["type"] == "image_url" for m in messages for p in m["content"])
    if n_images > MAX_IMAGES:
        raise gr.Error(f"Too many images in the conversation ({n_images}); the limit is {MAX_IMAGES}.")

    instance = {
        "@requestFormat": "chatCompletions",
        "messages": messages,
        "max_tokens": max_new_tokens,
        "temperature": temperature,
    }
    try:
        response = endpoint.predict(
            instances=[instance], use_dedicated_endpoint=DEDICATED_ENDPOINT, timeout=300
        )
    except Exception as e:
        raise gr.Error(f"Vertex AI request failed: {e}") from e
    return _extract_text(response.predictions)


demo = gr.ChatInterface(
    fn=generate,
    multimodal=True,
    textbox=gr.MultimodalTextbox(
        file_types=["image"], file_count="multiple", placeholder="Ask anything, or attach an image…"
    ),
    additional_inputs=[
        gr.Textbox(label="System prompt", value="You are a helpful assistant.", lines=2),
        gr.Slider(label="Max new tokens", minimum=64, maximum=2048, step=64, value=700),
        gr.Slider(label="Temperature (0 = greedy)", minimum=0.0, maximum=1.5, step=0.05, value=1.0),
    ],
    examples=[
        [{"text": "Explain the difference between a process and a thread in three sentences.", "files": []}],
        [{"text": "Write a haiku about autumn in Annecy.", "files": []}],
        [{"text": "Traduis en anglais : « Le savoir est une arme. »", "files": []}],
    ],
    cache_examples=False,
    title="Gemma 3 12B IT",
    description=(
        "Chat with [google/gemma-3-12b-it](https://huggingface.co/google/gemma-3-12b-it), "
        "served from a Vertex AI endpoint. Attach images to ask about them."
    ),
    fill_height=True,
)

if __name__ == "__main__":
    demo.launch()
