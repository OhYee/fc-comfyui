FROM python:3.10.9-slim 

RUN apt-get update
RUN apt-get install curl iputils-ping rsync vim git curl wget jq ffmpeg gcc g++ unzip build-essential -y

RUN pip install pip --upgrade

# cudann
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg2 curl ca-certificates && \
    curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub | apt-key add - && \
    echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    echo "deb https://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu2004/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list && \
    echo "deb [trusted=yes] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64 /" > /etc/apt/sources.list.d/cuda.list && \
    apt-get update && apt-get install -y --no-install-recommends \
    cuda-cudart-11-8 \
    libcudnn8=8.6.0.163-1+cuda11.8 \
    && rm -rf /var/lib/apt/lists/*

# python depencies

RUN pip install \
    "Pillow" \
    "PyGithub" \
    "accelerate" \
    "addict" \
    "aiohttp>=3.11.8" \
    "albumentations" \
    "av" \
    "boto3>=1.34.101" \
    "chardet" \
    "clip_interrogator>=0.6.0" \
    "comfyui-frontend-package==1.11.8" \
    "diffusers" \
    "einops" \
    "fairscale" \
    "filelock" \
    "ftfy" \
    "fvcore" \
    "huggingface-hub>0.20" \
    "huggingface_hub" \
    "importlib_metadata" \
    "iopath" \
    "kornia>=0.7.1" \
    "lark" \
    "matplotlib" \
    "matrix-client==0.4.0" \
    "mediapipe" \
    "numexpr" \
    "numpy>=1.25.0" \
    "omegaconf" \
    "onnxruntime" \
    "tensorrt" \
    "opencv-python>=4.7.0.72" \
    "pandas" \
    "peft" \
    "polygraphy" \
    "psutil" \
    "pycocoevalcap" \
    "pydantic" \
    "pytest-aiohttp" \
    "pytest-asyncio" \
    "pytest>=7.8.0" \
    "python-dateutil" \
    "pytorch_lightning" \
    "pyyaml" \
    "qrcode[pil]" \
    "rich" \
    "safetensors>=0.4.2" \
    "scikit-image" \
    "scikit-learn" \
    "scipy" \
    "segment_anything" \
    "sentencepiece" \
    "soundfile" \
    "spandrel" \
    "submitit" \
    "svglib" \
    "timm" \
    "tokenizers>=0.13.3" \
    "toml" \
    "tqdm" \
    "transformers>=4.28.1" \
    "trimesh[easy]" \
    "typer" \
    "typing-extensions" \
    "uv" \
    "yacs" \
    "yapf" \
    "yarl>=1.18.0"

RUN pip install \
    torch==2.5.0 \
    torchaudio \
    torchmetrics==0.10.3 \
    torchsde \
    torchvision \
    -f https://aiacc-inference-public-v2.oss-cn-hangzhou.aliyuncs.com/deepgpu/deepytorch/index.html \
    -f https://aiacc-inference-public-v2.oss-cn-hangzhou.aliyuncs.com/deepgpu/comfyui/index.html \
    -f https://aiacc-inference-public-v2.oss-accelerate.aliyuncs.com/aiacc-inference-torch/stable-diffusion/aiacctorch_stable-diffusion.html

RUN pip install cuml-cu11 --extra-index-url https://pypi.nvidia.com 
# RUN pip install xformers==0.0.18 --index-url https://download.pytorch.org/whl/cu126

ENV BUILTIN="/built-in"
ENV COMFYUI="/comfyui"
ENV NAS_DIR="/mnt/auto/comfyui"
ENV VIRTUAL_NAS="/virtual_nas"

RUN git clone https://github.com/comfyanonymous/ComfyUI.git ${COMFYUI} && \
    cd ${COMFYUI} && \
    git checkout v0.3.26

# custom nodes
# RUN mkdir -p ${BUILTIN}/custom_nodes && \ 
#     cd ${BUILTIN}/custom_nodes && \
#     git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
#     cd ComfyUI-Manager && \
#     git checkout 3.31.6

RUN mkdir -p ${BUILTIN}/custom_nodes && \ 
    cd ${BUILTIN}/custom_nodes && \
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux && \
    git clone https://github.com/yolain/ComfyUI-Easy-Use && \
    git clone https://github.com/twri/sdxl_prompt_styler && \
    git clone https://github.com/pythongosssss/ComfyUI-WD14-Tagger && \
    git clone https://github.com/FizzleDorf/ComfyUI_FizzNodes && \
    git clone https://github.com/JettHu/ComfyUI-TCD && \
    git clone https://github.com/yuvraj108c/ComfyUI-Depth-Anything-Tensorrt && \
    git clone https://github.com/hylarucoder/comfyui-copilot && \
    git clone https://github.com/sipherxyz/comfyui-art-venture 

# 加速能力
RUN pip install torch==2.5.0
RUN pip install deepgpu-torch==0.0.15+torch2.5.0cu124 -f https://aiacc-inference-public-v2.oss-cn-hangzhou.aliyuncs.com/deepgpu/deepytorch/index.html
RUN pip install deepgpu-comfyui==1.0.8 -f https://aiacc-inference-public-v2.oss-cn-hangzhou.aliyuncs.com/deepgpu/comfyui/index.html
RUN mkdir -p /built-in/custom_nodes && \
    wget https://aiacc-inference-public-v2.oss-cn-hangzhou.aliyuncs.com/deepgpu/comfyui/flux/20250102/ComfyUI-deepgpu.tar.gz && \
    tar zxf ComfyUI-deepgpu.tar.gz -C ${BUILTIN}/custom_nodes && \
    rm ComfyUI-deepgpu.tar.gz
RUN sed -i ${COMFYUI}/comfy/sd.py -e '/model_patcher =.*unet_offload_device/{s/))/), weight_inplace_update=True)/;}'


RUN mkdir -p /built-in/custom_nodes/ComfyUI-WD14-Tagger/models/ && \
    curl -Lo /built-in/custom_nodes/ComfyUI-WD14-Tagger/models/wd-vit-tagger-v3.onnx "https://huggingface.co/SmilingWolf/wd-vit-tagger-v3/resolve/main/model.onnx?download=true" && \
    curl -Lo /built-in/custom_nodes/ComfyUI-WD14-Tagger/models/wd-vit-tagger-v3.csv "https://huggingface.co/SmilingWolf/wd-vit-tagger-v3/resolve/main/selected_tags.csv?download=true"
RUN mkdir -p /built-in/custom_nodes/comfyui_controlnet_aux/ckpts/LiheYoung/Depth-Anything/checkpoints && \
    curl -Lo /built-in/custom_nodes/comfyui_controlnet_aux/ckpts/LiheYoung/Depth-Anything/checkpoints/depth_anything_vitl14.pth "https://huggingface.co/LiheYoung/depth_anything_vitl14/resolve/main/pytorch_model.bin?download=true"

ENV DEEPGPU_PUB_LS=true
ENV DEEPGPU_ENABLE_FLUX_LORA=true
# ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

RUN mkdir -p ${BUILTIN}/models/tensorrt/depth-anything

RUN --mount=type=bind,source=./,target=/docker \
    bash /docker/init.bash

COPY ./agent /agent
RUN pip3 install -r /agent/requirements.txt

ENTRYPOINT [ "/entrypoint.bash" ]
COPY ./entrypoint.bash /entrypoint.bash






