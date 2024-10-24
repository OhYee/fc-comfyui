FROM python:3.10.9-slim AS deps

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
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
    kornia>=0.7.1 && \
    pip install --no-cache-dir onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/

FROM alpine/git:2.36.2 AS repos

RUN git clone https://github.com/comfyanonymous/ComfyUI.git /code && \
    cd /code && \
    git checkout v0.2.2

FROM alpine/git:2.36.2 AS custom_nodes

WORKDIR /custom_nodes

RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    git checkout "584c5002477e5cc88b56fe02853a4e7c43660bbf"

RUN --mount=type=bind,source=/base/v5/built-in,target=/docker \
    cp -R /docker/custom_nodes/* /custom_nodes/

FROM python:3.10.9-slim AS models

RUN apt update && apt install -y aria2

COPY --from=registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-sd1.5-v1 "/built-in/models/checkpoints/sd-v1-5-inpainting.ckpt" "/models/checkpoints/sd-v1-5-inpainting.ckpt"



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
    rsync vim git curl wget jq ffmpeg \
    gcc g++ unzip build-essential
    libgl1-mesa-glx freeglut3-dev

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
    pip install --upgrade pip && \
    pip install -r ${COMFYUI}/requirements.txt --no-cache-dir && \ 
    find ${COMFYUI} -type f -name requirements.txt | xargs -I {} pip install -r {}

# 移动自带文件
RUN mkdir -p ${BUILTIN}/custom_nodes && \
    rsync -av --remove-source-files ${COMFYUI}/custom_nodes/ ${BUILTIN}/custom_nodes

ENTRYPOINT [ "/entrypoint.bash" ]





# lite 轻量版镜像
FROM base AS lite

# 处理文件关系
ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

RUN --mount=type=bind,from=agent,source=/agent,target=/mnt/agent \
    --mount=type=bind,source=/base/v5,target=/docker \
    bash /docker/init.bash




# sd1.5 内置 sd1.5 模型及推荐自定义节点的镜像
FROM base AS sd1.5

# 内置模型
RUN --mount=type=bind,from=models,source=/models,target=/models \
    mkdir -p ${BUILTIN}/models/checkpoints && \
    rsync -av /models/ ${BUILTIN}/models/

# 内置自定义节点
RUN --mount=type=bind,from=custom_nodes,source=/custom_nodes,target=/custom_nodes \
    --mount=type=bind,source=./,target=/docker \
    mkdir -p ${BUILTIN}/custom_nodes && \
    rsync -av /custom_nodes/ ${BUILTIN}/custom_nodes

# 更新依赖至最新
RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes -type f -name requirements.txt | xargs -I {} pip install -r {}


# 处理文件关系
ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

RUN --mount=type=bind,from=agent,source=/agent,target=/mnt/agent \
    --mount=type=bind,source=/base/v5,target=/docker \
    bash /docker/init.bash
