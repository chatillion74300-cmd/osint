"""Gradio demo for google/gemma-3-12b-it (text + image chat) on Hugging Face ZeroGPU."""

import os
from threading import Thread

import gradio as gr
import spaces
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor, TextIteratorStreamer

MODEL_ID = os.getenv("MODEL_ID", "google/gemma-3-12b-it")
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
MAX_IMAGES = 5

processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID, device_map="auto", dtype=torch.bfloat16
)
model.eval()


def _is_image(path: str) -> bool:
    return path.lower().endswith(IMAGE_EXTENSIONS)


def _to_parts(content) -> list[dict]:
    """Convert any Gradio chat content shape into Gemma chat-template parts."""
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
        if path and _is_image(path):
            return [{"type": "image", "url": path}]
        return []
    path = getattr(content, "path", None)  # gr.FileData
    if path and _is_image(path):
        return [{"type": "image", "url": path}]
    return []


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


@spaces.GPU(duration=120)
def generate(message: dict, history: list[dict], system_prompt: str, max_new_tokens: int, temperature: float):
    messages = build_messages(message, history, system_prompt)

    n_images = sum(p["type"] == "image" for m in messages for p in m["content"])
    if n_images > MAX_IMAGES:
        raise gr.Error(f"Too many images in the conversation ({n_images}); the limit is {MAX_IMAGES}.")

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device, dtype=torch.bfloat16)

    streamer = TextIteratorStreamer(processor, skip_prompt=True, skip_special_tokens=True, timeout=60.0)
    generate_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=temperature > 0,
    )
    if temperature > 0:
        generate_kwargs.update(temperature=temperature, top_p=0.95, top_k=64)

    thread = Thread(target=model.generate, kwargs=generate_kwargs)
    thread.start()

    output = ""
    for chunk in streamer:
        output += chunk
        yield output
    thread.join()


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
        "Google's 12B instruction-tuned multimodal model. Attach images to ask about them."
    ),
    stop_btn=True,
    fill_height=True,
)

if __name__ == "__main__":
    demo.launch()
