"""Gradio demo for the DeepBeepMeep/Wan2.1 checkpoints, driven through the WanGP Python API.

This demo uses WanGP (https://github.com/deepbeepmeep/Wan2GP).
"""

import os
import random
import sys
import threading
from pathlib import Path

import gradio as gr

WANGP_ROOT = Path(os.environ.get("WANGP_ROOT", "/home/user/Wan2GP"))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/tmp/wangp_outputs"))
ENABLE_14B = os.environ.get("ENABLE_14B", "0") == "1"
MAX_FRAMES = int(os.environ.get("MAX_FRAMES", "81"))
CLI_ARGS = [
    "--attention", os.environ.get("WANGP_ATTENTION", "sdpa"),
    "--profile", os.environ.get("WANGP_PROFILE", "4"),
]

MODELS = {"Wan2.1 Text2Video 1.3B": "t2v_1.3B"}
if ENABLE_14B:
    MODELS["Wan2.1 Text2Video 14B"] = "t2v"
    MODELS["Wan2.1 Image2Video 480p 14B"] = "i2v"

RESOLUTIONS = ["832x480", "480x832", "720x720", "672x384"]
OUTPUT_KINDS = ["Video", "Image"]
# Image mode renders a short clip and keeps its middle frame (Wan2.1 T2V has no native image output in WanGP).
IMAGE_MODE_FRAMES = 17
DEFAULT_NEGATIVE = (
    "blurry, low quality, distorted, deformed, watermark, text, static, overexposed"
)

sys.path.insert(0, str(WANGP_ROOT))

_session = None
_session_lock = threading.Lock()


def _link_persistent_storage():
    """Keep downloaded checkpoints on /data when persistent storage is attached."""
    data = Path("/data")
    ckpts = WANGP_ROOT / "ckpts"
    if not data.is_dir() or ckpts.is_symlink():
        return
    target = data / "ckpts"
    target.mkdir(parents=True, exist_ok=True)
    if ckpts.exists():
        for item in ckpts.iterdir():
            item.rename(target / item.name)
        ckpts.rmdir()
    ckpts.symlink_to(target, target_is_directory=True)


def get_session():
    global _session
    with _session_lock:
        if _session is None:
            _link_persistent_storage()
            from shared.api import init

            _session = init(root=WANGP_ROOT, output_dir=OUTPUT_DIR, cli_args=CLI_ARGS)
        return _session


def _extract_frame(video_path):
    import imageio.v2 as imageio

    reader = imageio.get_reader(video_path)
    try:
        frames = [frame for frame in reader]
    finally:
        reader.close()
    if not frames:
        raise gr.Error("The generated clip has no frames.")
    image_path = str(Path(video_path).with_suffix(".png"))
    imageio.imwrite(image_path, frames[len(frames) // 2])
    return image_path


class _ProgressCallbacks:
    def __init__(self, progress):
        self.progress = progress
        self.ratio = 0.0

    def on_status(self, status):
        status = str(status or "").strip()
        if status:
            self.progress(self.ratio, desc=status)

    def on_progress(self, update):
        self.ratio = max(0.0, min(1.0, float(getattr(update, "progress", 0) or 0) / 100.0))
        self.progress(self.ratio, desc=str(getattr(update, "status", "") or "Generating..."))


def generate(output_kind, model_label, prompt, image, negative_prompt, resolution, frames,
             steps, guidance, seed, randomize_seed, progress=gr.Progress(track_tqdm=False)):
    if not prompt or not prompt.strip():
        raise gr.Error("Please enter a prompt.")
    model_type = MODELS[model_label]
    if model_type == "i2v" and image is None:
        raise gr.Error("Image2Video needs a start image.")
    if randomize_seed:
        seed = random.randint(0, 2**31 - 1)
    image_mode = output_kind == "Image"
    if image_mode:
        frames = IMAGE_MODE_FRAMES

    progress(0, desc="Loading WanGP (first run downloads checkpoints, this can take a while)...")
    session = get_session()

    settings = session.get_default_settings(model_type)
    settings.update({
        "model_type": model_type,
        "prompt": prompt.strip(),
        "negative_prompt": negative_prompt or "",
        "resolution": resolution,
        "video_length": int(frames),
        "num_inference_steps": int(steps),
        "guidance_scale": float(guidance),
        "seed": int(seed),
    })
    if model_type == "i2v":
        settings["image_prompt_type"] = "S"
        settings["image_start"] = image

    job = session.submit_task(settings, callbacks=_ProgressCallbacks(progress))
    result = job.result()
    if not result.success or not result.generated_files:
        message = "; ".join(e.message for e in result.errors) or "Generation failed."
        raise gr.Error(message)
    output = result.generated_files[-1]
    if image_mode:
        return gr.update(value=None, visible=False), gr.update(value=_extract_frame(output), visible=True), int(seed)
    return gr.update(value=output, visible=True), gr.update(value=None, visible=False), int(seed)


def _toggle_image(model_label):
    return gr.update(visible=MODELS[model_label] == "i2v")


def _toggle_output(output_kind):
    return gr.update(visible=output_kind == "Video")


with gr.Blocks(title="Wan2.1 Video Demo") as demo:
    gr.Markdown(
        "# Wan2.1 Video Demo\n"
        "Weights: [DeepBeepMeep/Wan2.1](https://huggingface.co/DeepBeepMeep/Wan2.1) · "
        "Runtime: this demo uses [WanGP](https://github.com/deepbeepmeep/Wan2GP). "
        "The first generation downloads the checkpoints and is slow."
    )
    with gr.Row():
        with gr.Column():
            output_kind = gr.Radio(OUTPUT_KINDS, value="Video", label="Output")
            model = gr.Dropdown(list(MODELS), value=next(iter(MODELS)), label="Model")
            prompt = gr.Textbox(
                label="Prompt", lines=3,
                value="A red fox trotting through fresh snow in a pine forest at sunrise, cinematic",
            )
            image = gr.Image(label="Start image", type="filepath", visible=False)
            with gr.Accordion("Advanced settings", open=False):
                negative = gr.Textbox(label="Negative prompt", value=DEFAULT_NEGATIVE)
                resolution = gr.Dropdown(RESOLUTIONS, value=RESOLUTIONS[0], label="Resolution")
                frames = gr.Slider(17, MAX_FRAMES, value=min(49, MAX_FRAMES), step=4,
                                   label="Frames (16 fps)")
                steps = gr.Slider(4, 50, value=30, step=1, label="Inference steps")
                guidance = gr.Slider(1.0, 10.0, value=5.0, step=0.5, label="Guidance scale")
                with gr.Row():
                    seed = gr.Number(value=42, precision=0, label="Seed")
                    randomize = gr.Checkbox(value=True, label="Randomize seed")
            run = gr.Button("Generate", variant="primary")
        with gr.Column():
            video = gr.Video(label="Result", autoplay=True)
            result_image = gr.Image(label="Result", type="filepath", format="png", visible=False)
            used_seed = gr.Number(label="Seed used", interactive=False)

    model.change(_toggle_image, model, image)
    output_kind.change(_toggle_output, output_kind, frames)
    run.click(
        generate,
        [output_kind, model, prompt, image, negative, resolution, frames, steps, guidance, seed,
         randomize],
        [video, result_image, used_seed],
        concurrency_limit=1,
    )

if __name__ == "__main__":
    # Load the WanGP runtime in the main thread before serving; models load on first generation.
    get_session()
    demo.queue(max_size=8).launch(server_name="0.0.0.0", server_port=7860)
