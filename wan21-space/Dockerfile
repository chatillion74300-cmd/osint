FROM python:3.11-slim

ARG WANGP_COMMIT=9d25c601f3c7074ca03c50f41b307a7c517835f9

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ffmpeg libgl1 libglib2.0-0 build-essential \
    && rm -rf /var/lib/apt/lists/*

# Spaces run as uid 1000
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    SDL_AUDIODRIVER=dummy \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    WANGP_ROOT=/home/user/Wan2GP
WORKDIR /home/user

RUN git clone https://github.com/deepbeepmeep/Wan2GP.git "$WANGP_ROOT" \
    && git -C "$WANGP_ROOT" checkout "$WANGP_COMMIT"

# Same torch build as WanGP's own Dockerfile (CUDA 12.8 wheels bundle the CUDA runtime)
RUN pip install --no-cache-dir --user \
        torch==2.10.0+cu128 torchvision==0.25.0+cu128 torchaudio==2.10.0+cu128 \
        --index-url https://download.pytorch.org/whl/cu128
RUN pip install --no-cache-dir --user -r "$WANGP_ROOT/requirements.txt"

COPY --chown=user app.py /home/user/app/app.py
WORKDIR /home/user/app

EXPOSE 7860
CMD ["python", "app.py"]
