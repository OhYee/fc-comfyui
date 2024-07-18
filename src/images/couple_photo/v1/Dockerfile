ARG BASE_IMAGE

FROM python:3.10.9-slim AS models

RUN apt update && apt install -y aria2

# https://github.com/cubiq/ComfyUI_IPAdapter_plus
# RUN aria2c -x 16 --dir "/models/clip_vision" --out "CLIP-ViT-bigG-14-laion2B-39B-b160k.safetensors" "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/image_encoder/model.safetensors"
RUN aria2c -x 16 --dir "/models/clip_vision" --out "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors"
# RUN aria2c -x 16 --dir "/models/ipadapter" --out "ip-adapter-plus_sdxl_vit-h.safetensors" "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors"
RUN aria2c -x 16 --dir "/models/ipadapter" --out "ip-adapter-plus_sd15.safetensors" "https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors"

# controlnet openpose
RUN aria2c -x 16 --dir "/models/controlnet" --out "control_v11p_sd15_openpose_fp16.safetensors" "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_openpose_fp16.safetensors?download=true"
RUN aria2c -x 16 --dir "/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators" --out "body_pose_model.pth" "https://huggingface.co/lllyasviel/Annotators/resolve/main/body_pose_model.pth?download=true"
RUN aria2c -x 16 --dir "/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators" --out "hand_pose_model.pth" "https://huggingface.co/lllyasviel/Annotators/resolve/main/hand_pose_model.pth?download=true"
RUN aria2c -x 16 --dir "/custom_nodes/comfyui_controlnet_aux/ckpts/lllyasviel/Annotators" --out "facenet.pth" "https://huggingface.co/lllyasviel/Annotators/resolve/main/facenet.pth?download=true"

# WD14 Tagger
RUN aria2c -x 16 --dir "/custom_nodes/ComfyUI-WD14-Tagger/models" --out "wd-v1-4-moat-tagger-v2.onnx" "https://huggingface.co/SmilingWolf/wd-v1-4-moat-tagger-v2/resolve/main/model.onnx?download=true"
RUN aria2c -x 16 --dir "/custom_nodes/ComfyUI-WD14-Tagger/models" --out "wd-v1-4-moat-tagger-v2.csv" "https://huggingface.co/SmilingWolf/wd-v1-4-moat-tagger-v2/resolve/main/selected_tags.csv?download=true"

# insightface
RUN aria2c -x 16 --dir "/models/insightface/models/" --out "buffalo_l.zip" "https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip"
RUN apt update && apt install unzip -y && unzip -d /models/insightface/models/buffalo_l /models/insightface/models/buffalo_l.zip

# 基础模型
RUN aria2c -x 16 --dir "/models/checkpoints" --out "majicMIX realistic_v7.safetensors" "https://civitai.com/api/download/models/176425?type=Model&format=SafeTensor&size=pruned&fp=fp16"

RUN aria2c -x 16 --dir "/models/rembg" --out "RMBG-1.4.pth" "https://huggingface.co/briaai/RMBG-1.4/resolve/main/model.pth"


FROM alpine/git:2.36.2 AS custom_nodes

WORKDIR /custom_nodes

RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    git checkout 02b2bf96d24ed6297dad8f676aa68d7512a166b3

RUN git clone https://github.com/cubiq/ComfyUI_essentials.git && \
    cd ComfyUI_essentials && \
    git checkout c26bc23d53c1953dca5697b211d6f9a51c4d607e

RUN git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git && \
    cd ComfyUI_IPAdapter_plus && \
    git checkout 20125bf9394b1bc98ef3228277a31a3a52c72fc2

RUN git clone https://github.com/Acly/comfyui-tooling-nodes.git && \
    cd comfyui-tooling-nodes && \
    git checkout 9d533984c2b44bc0519fde2875b976493c6e90a0

RUN git clone https://github.com/pythongosssss/ComfyUI-WD14-Tagger.git && \
    cd ComfyUI-WD14-Tagger && \
    git checkout 4f1a857ff1a73ad2b4cbaf1f487e6aeaf802d226

RUN git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git && \
    cd comfyui_controlnet_aux && \
    git checkout 3c1d9de28afd59392c07f8419c14998df2b9204a

RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git && \
    cd ComfyUI-Easy-Use && \
    git checkout f5219ab51624ca71b9ec581bc0703630dd897cbf

RUN git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git && \
    cd ComfyUI_Comfyroll_CustomNodes && \
    git checkout d78b780ae43fcf8c6b7c6505e6ffb4584281ceca


FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-lite-v3

# 内置模型
RUN --mount=type=bind,from=models,source=/models,target=/models \
    --mount=type=bind,from=models,source=/custom_nodes,target=/custom_nodes \
    mkdir -p ${BUILTIN}/models/checkpoints ${BUILTIN}/models/loras ${BUILTIN}/custom_nodes && \
    rsync -a --ignore-existing /models/* ${BUILTIN}/models/ && \
    rsync -a --ignore-existing /custom_nodes/* ${BUILTIN}/custom_nodes/

# 内置自定义节点
RUN --mount=type=bind,from=custom_nodes,source=/custom_nodes,target=/custom_nodes \
    mkdir -p ${BUILTIN}/custom_nodes && \
    rsync -a --ignore-existing /custom_nodes/* ${BUILTIN}/custom_nodes

# 将 venv 指回到容器内
RUN grep -r "/venv" /venv/bin/* | awk -F: "{print \$1}" | xargs -I {} sed "s@${NAS_DIR}/venv@/venv@g" -i {}

# 更新依赖至最新
RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes -maxdepth 2 -type f -name requirements.txt | xargs -I {} pip install  -r {} && \
    pip install insightface

# 内置文件
RUN --mount=type=bind,source=/clay/v1/built-in,target=/docker \
    mkdir -p ${BUILTIN}/input/ && \
    rsync -a --ignore-existing /docker/input/* ${BUILTIN}/input/

ARG IMAGE_TAG=${IMAGE_TAG}
ENV IMAGE_TAG=${IMAGE_TAG}
RUN --mount=type=bind,source=/base/v3,target=/docker \
    mkdir -p ${COMFYUI}/models/configs && \
    bash /docker/init.bash

