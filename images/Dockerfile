FROM python:3.10.9-slim as deps

RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir \
    torch \
    torchsde \
    torchvision \
    einops \
    transformers>=4.25.1 \
    safetensors>=0.3.0 \
    aiohttp \
    pyyaml \
    Pillow \
    scipy \
    tqdm \
    psutil \
    kornia>=0.7.1

FROM alpine/git:2.36.2 as repos

RUN git clone https://github.com/comfyanonymous/ComfyUI.git /code && \
    cd /code && \
    git checkout 0a03009808a5ad13fa3a44edbabcae68576c3982 && \
    rm -rf .git

FROM alpine/git:2.36.2 as custom_nodes

WORKDIR /custom_nodes

RUN git clone https://github.com/11cafe/comfyui-workspace-manager.git && \
    cd comfyui-workspace-manager && \
    git checkout 5dc8ab668fc330300a8b43a1687dbe7f5230b4fe && \
    rm -rf .git

RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    git checkout 02b2bf96d24ed6297dad8f676aa68d7512a166b3 && \
    rm -rf .git

FROM python:3.10.9-slim as models

RUN apt update && apt install -y aria2

RUN aria2c -x 16 --dir "/models" --out "sd-v1-5-inpainting.ckpt" "https://huggingface.co/runwayml/stable-diffusion-inpainting/resolve/main/sd-v1-5-inpainting.ckpt"


FROM python:3.10.9-slim as base

ENV BUILTIN="/built-in"
ENV COMFYUI="/comfyui"
ENV NAS_DIR="/mnt/auto/comfyui"
ENV VIRTUAL_NAS="/virtual_nas"

RUN --mount=type=cache,target=/var/cache/apt \
    apt update && \
    apt install -y \
    rsync vim git curl wget jq ffmpeg \
    gcc g++ unzip build-essential

# 从依赖镜像获取所需的依赖文件，并映射至 /mnt/auto/comfyui
RUN --mount=type=bind,from=deps,source=/venv,target=/comfyui_venv \
    mkdir -p /venv && \
    cp -R /comfyui_venv/* /venv

# 获取 ComfyUI 代码
RUN --mount=type=bind,from=repos,source=/code,target=/code \
    mkdir -p ${COMFYUI} && \
    cp -R /code/* ${COMFYUI} 

# 使用 venv 环境
ENV VIRTUAL_ENV="/venv"
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

WORKDIR ${COMFYUI}

# 确保依赖最新
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r ${COMFYUI}/requirements.txt --no-cache-dir && \ 
    find ${COMFYUI} -type f -name requirements.txt | xargs -I {} pip install -r {}

# 移动自带文件
RUN mkdir -p ${BUILTIN}/custom_nodes && \
    mv ${COMFYUI}/custom_nodes/* ${BUILTIN}/custom_nodes


ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

ENTRYPOINT [ "/entrypoint.bash" ]

FROM base as builtin

COPY . /docker

# lite 轻量版镜像
FROM base as lite

RUN --mount=type=bind,from=builtin,source=/docker,target=/docker \
    bash /docker/init.bash

# sd1.5 内置 sd1.5 模型及推荐自定义节点的镜像
FROM base as sd1.5

# 内置模型
RUN --mount=type=bind,from=models,source=/models,target=/models \
    mkdir -p ${BUILTIN}/models/checkpoints && \
    cp -R /models/* ${BUILTIN}/models/checkpoints

# 内置自定义节点
RUN --mount=type=bind,from=custom_nodes,source=/custom_nodes,target=/custom_nodes \
    mkdir -p ${BUILTIN}/custom_nodes && \
    cp -R /custom_nodes/* ${BUILTIN}/custom_nodes

# 更新依赖至最新
RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes -type f -name requirements.txt | xargs -I {} pip install -r {}

RUN --mount=type=bind,from=builtin,source=/docker,target=/docker \
    bash /docker/init.bash
