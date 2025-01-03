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
    numpy==1.26.4 \
    matplotlib \
    kornia>=0.7.1 && \
    pip install --no-cache-dir onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/


FROM alpine/git:2.36.2 AS repos

RUN git clone https://github.com/comfyanonymous/ComfyUI.git /code && \
    cd /code && \
    git checkout "9a616b8"

FROM alpine/git:2.36.2 AS custom_nodes

WORKDIR /custom_nodes

# RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
#     cd ComfyUI-Manager && \
#     git checkout "9e44617"

# ComfyUI_FizzNodes
RUN git clone https://github.com/FizzleDorf/ComfyUI_FizzNodes.git

# ComfyUI-Easy-Use
RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git && \
    cd ComfyUI-Easy-Use && \
    git checkout "d416ad2"

# ComfyUI-Custom-Scripts
RUN git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git

# ComfyUI_Comfyroll_CustomNodes
RUN git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git

# ComfyUI-Universal-Styler
RUN git clone https://github.com/KoreTeknology/ComfyUI-Universal-Styler.git

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
    rsync git \
    # libglib2.0-dev
    ffmpeg \
    libsm6 \
    libxext6
    

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

# flux
RUN aria2c -x 16 --dir "/models/unet" --out "flux1-schnell-fp8-e4m3fn.safetensors" "https://huggingface.co/Kijai/flux-fp8/resolve/main/flux1-schnell-fp8-e4m3fn.safetensors?download=true"

# 335 MB
RUN aria2c -x 16 --dir "/models/vae" --out "ae.safetensors" "https://huggingface.co/lovis93/testllm/resolve/main/ae.safetensors?download=true"

# https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf/tree/main 4.89G
RUN aria2c -x 16 --dir "/models/clip" --out "t5xxl_fp8_e4m3fn.safetensors" "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors?download=true"

# https://huggingface.co/comfyanonymous/flux_text_encoders/tree/main 323M
RUN aria2c -x 16 --dir "/models/clip" --out "clip_l.safetensors" "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors?download=true"

# diffusion_pytorch_model.safetensors
RUN aria2c -x 16 --dir "/models/loras" --out "diffusion_pytorch_model.safetensors" "https://huggingface.co/alimama-creative/FLUX.1-Turbo-Alpha/resolve/main/diffusion_pytorch_model.safetensors?download=true"


FROM base

# 内置模型
# RUN --mount=type=bind,from=registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-flux-v1,source=${BUILTIN}/models,target=/models \
#     mkdir -p ${BUILTIN}/models/checkpoints ${BUILTIN}/models/loras ${BUILTIN}/models/unet && \
#     cp /models/checkpoints/flux1-dev-fp8.safetensors ${BUILTIN}/models/unet
RUN --mount=type=bind,from=models,source=/models,target=/models \
    mkdir -p ${BUILTIN}/models/unet && \
    cp /models/unet/flux1-schnell-fp8-e4m3fn.safetensors ${BUILTIN}/models/unet

RUN --mount=type=bind,from=models,source=/models,target=/models \
    mkdir -p ${BUILTIN}/models/checkpoints ${BUILTIN}/models/loras ${BUILTIN}/models/unet && \
    rsync -a --ignore-existing /models/* ${BUILTIN}/models/


# # 内置插件(费用提醒插件)
RUN --mount=type=bind,source=/base/v6,target=/docker \
    cp -R /docker/built-in/custom_nodes/* ${BUILTIN}/custom_nodes/

# 内置自定义节点
RUN --mount=type=bind,from=custom_nodes,source=/custom_nodes,target=/custom_nodes \
    --mount=type=bind,source=./,target=/docker \
    mkdir -p ${BUILTIN}/custom_nodes && \
    rsync -av /custom_nodes/ ${BUILTIN}/custom_nodes

# 内置文件
RUN --mount=type=bind,source=/book/v5/built-in,target=/docker \
    mkdir -p /comfyui/user/default/workflows/ && \
    cp -R /docker/* /comfyui/user/default/workflows/

# 更新依赖至最新
RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes -type f -name requirements.txt | xargs -I {} pip install -r {}


ARG IMAGE_TAG=${IMAGE_TAG}
ENV IMAGE_TAG=${IMAGE_TAG}
RUN --mount=type=bind,from=agent,source=/agent,target=/mnt/agent \
    --mount=type=bind,source=/base/v6,target=/docker \
    bash /docker/init.bash