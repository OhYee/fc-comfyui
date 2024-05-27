ARG BASE_IMAGE

FROM python:3.10.9-slim as models

RUN apt update && apt install -y aria2

# https://huggingface.co/lllyasviel/sd_control_collection/tree/7cf256327b341fedc82e00b0d7fb5481ad693210
RUN aria2c -x 16 --dir "/models/controlnet" --out "sai_xl_canny_256lora.safetensors" "https://huggingface.co/lllyasviel/sd_control_collection/resolve/7cf256327b341fedc82e00b0d7fb5481ad693210/sai_xl_canny_256lora.safetensors?download=true"

# https://github.com/cubiq/ComfyUI_IPAdapter_plus
# RUN aria2c -x 16 --dir "/models/clip_vision" --out "CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors" "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors"
RUN aria2c -x 16 --dir "/models/clip_vision" --out "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors"
RUN aria2c -x 16 --dir "/models/ipadapter" --out "ip-adapter-plus_sdxl_vit-h.safetensors" "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors"

# https://civitai.com/models/155404/sdxl-anime-or (old version)
RUN aria2c -x 16 --dir "/models/checkpoints" --out "Anime天空之境SDXL.safetensors" "https://server-ai-backend-agwwspzdwb.cn-hangzhou.devsapp.net/oss_models/url/public/data-oss/models/Stable-diffusion/Anime天空之境SDXL.safetensors"

# https://civitai.com/models/208168/claymate-claymation-style-for-sdxl
RUN aria2c -x 16 --dir "/models/loras" --out "claymateV203.gkfW.safetensors" "https://civitai-delivery-worker-prod.5ac0637cfd0766c97916cefa3764fbdf.r2.cloudflarestorage.com/model/2906/claymateV203.gkfW.safetensors?X-Amz-Expires=86400&response-content-disposition=attachment%3B%20filename%3D%22CLAYMATE_V2.03_.safetensors%22&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=e01358d793ad6966166af8b3064953ad/20240522/us-east-1/s3/aws4_request&X-Amz-Date=20240522T071035Z&X-Amz-SignedHeaders=host&X-Amz-Signature=d6bb9a5257f9b7f9ec37acee3011a2ed0ce99c367e20cb95c00bf8363df66ca1"


FROM alpine/git:2.36.2 as custom_nodes

WORKDIR /custom_nodes

RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    git checkout 02b2bf96d24ed6297dad8f676aa68d7512a166b3 && \
    rm -rf .git

RUN git clone https://github.com/cubiq/ComfyUI_essentials.git && \
    cd ComfyUI_essentials && \
    git checkout c26bc23d53c1953dca5697b211d6f9a51c4d607e && \
    rm -rf .git

RUN git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git && \
    cd ComfyUI_IPAdapter_plus && \
    git checkout 20125bf9394b1bc98ef3228277a31a3a52c72fc2 && \
    rm -rf .git

FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-lite-v2

# 内置模型
RUN --mount=type=bind,from=models,source=/models,target=/models \
    mkdir -p ${BUILTIN}/models/checkpoints ${BUILTIN}/models/loras && \
    rsync -a --ignore-existing /models/* ${BUILTIN}/models/

# 内置自定义节点
RUN --mount=type=bind,from=custom_nodes,source=/custom_nodes,target=/custom_nodes \
    mkdir -p ${BUILTIN}/custom_nodes && \
    cp -R /custom_nodes/* ${BUILTIN}/custom_nodes

# 将 venv 指回到容器内
RUN grep -r "/venv" /venv/bin/* | awk -F: "{print \$1}" | xargs -I {} sed "s@${NAS_DIR}/venv@/venv@g" -i {}

# 更新依赖至最新
RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes -type f -name requirements.txt | xargs -I {} pip install -r {}

# 内置文件
RUN --mount=type=bind,source=/clay/v1/built-in,target=/docker \
    mkdir -p ${BUILTIN}/input/ && \
    cp -R /docker/input/* ${BUILTIN}/input/

ARG IMAGE_TAG=${IMAGE_TAG}
ENV IMAGE_TAG=${IMAGE_TAG}
RUN --mount=type=bind,source=/base/v2,target=/docker \
    mkdir -p ${COMFYUI}/models/configs && \
    bash /docker/init.bash

