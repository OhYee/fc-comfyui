FROM python:3.10.9-slim AS deps

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

FROM alpine/git:2.36.2 AS repos

RUN git clone https://github.com/comfyanonymous/ComfyUI.git /code && \
    cd /code && \
    git checkout 0f9c2a78224ce3179c773fe3af63722f438b0613

FROM alpine/git:2.36.2 AS custom_nodes

WORKDIR /custom_nodes

RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    git checkout ef943a588df8ad9af1ddc6f3673ee456dcfb289e


FROM golang:1.21 AS agent

COPY agent /code
RUN cd /code
WORKDIR /code
RUN go get
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /agent main.go

ARG BASE_IMAGE

FROM python:3.10.9-slim AS base

ENV BUILTIN="/built-in"
ENV COMFYUI="/comfyui"
ENV NAS_DIR="/mnt/auto/comfyui"
ENV VIRTUAL_NAS="/virtual_nas"

RUN --mount=type=cache,target=/var/cache/apt \
    apt update && \
    apt install -y \
    rsync git

# 从依赖镜像获取所需的依赖文件，并映射至 /mnt/auto/comfyui
RUN --mount=type=bind,from=deps,source=/venv,target=/comfyui_venv \
    mkdir -p /venv && \
    rsync -av /comfyui_venv/ /venv

# 获取 ComfyUI 代码
RUN --mount=type=bind,from=repos,source=/code,target=/code \
    mkdir -p ${COMFYUI} && \
    rsync -av /code/ ${COMFYUI}

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
    rsync -av --remove-source-files ${COMFYUI}/custom_nodes/ ${BUILTIN}/custom_nodes

ENTRYPOINT [ "/entrypoint.bash" ]



FROM python:3.10.9-slim AS models

RUN apt update && apt install -y aria2

# https://huggingface.co/lllyasviel/flux1_dev/tree/main
RUN aria2c -x 16 --dir "/models/checkpoints" --out "flux1-dev-fp8.safetensors" "https://huggingface.co/lllyasviel/flux1_dev/resolve/main/flux1-dev-fp8.safetensors?download=true"



FROM base

# 内置模型
RUN --mount=type=bind,from=models,source=/models,target=/models \
    mkdir -p ${BUILTIN}/models/checkpoints ${BUILTIN}/models/loras && \
    rsync -a --ignore-existing /models/* ${BUILTIN}/models/

# 内置插件(费用提醒插件)
RUN --mount=type=bind,source=/base/v4,target=/docker \
    cp -R /docker/built-in/custom_nodes/* ${BUILTIN}/custom_nodes/

# 内置自定义节点
RUN --mount=type=bind,from=custom_nodes,source=/custom_nodes,target=/custom_nodes \
    --mount=type=bind,source=./,target=/docker \
    mkdir -p ${BUILTIN}/custom_nodes && \
    rsync -av /custom_nodes/ ${BUILTIN}/custom_nodes

# 更新依赖至最新
RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes -type f -name requirements.txt | xargs -I {} pip install -r {}


ARG IMAGE_TAG=${IMAGE_TAG}
ENV IMAGE_TAG=${IMAGE_TAG}
RUN --mount=type=bind,from=agent,source=/agent,target=/agent \
    --mount=type=bind,source=/base/v4,target=/docker \
    bash /docker/init.bash

