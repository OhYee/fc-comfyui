FROM python:3.10.16-slim

WORKDIR /root

RUN --mount=type=cache,target=/var/cache/apt \
    apt update && \
    apt install -y \
    git curl wget jq ffmpeg gcc g++ build-essential libgl1 libglib2.0-0

ENV WORK_DIR='/root'
ENV COMFYUI_DIR="${WORK_DIR}/comfyui"
ENV SD_DIR="${WORK_DIR}/stable-diffusion-webui"
ENV VENV_DIR="${WORK_DIR}/venv"
ENV AGENT_DIR="${WORK_DIR}/agent"
# MNT_DIR is initialized in s.yaml, using env var-'MODEL_ASSET_DIR'

COPY . ${AGENT_DIR}/
RUN pip3 install -r /agent/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    python3 -m venv ${AGENT_DIR}/venv

RUN --mount=type=cache,target=/root/.cache/pip \
    ${AGENT_DIR}/venv/bin/pip install -r ${AGENT_DIR}/requirements.txt --no-cache-dir

RUN chmod +x ${AGENT_DIR}/entrypoint.bash
ENTRYPOINT [ "/bin/bash", "-c", "agent/entrypoint.bash" ]
