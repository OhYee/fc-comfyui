ARG BASE_IMAGE

FROM python:3.10.9-slim AS models

RUN apt update && apt install -y aria2

RUN aria2c -x 16 --dir "/models/checkpoints" --out "sd_xl_turbo_1.0_fp16.safetensors" "https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors?download=true"

RUN aria2c -x 16 --dir "/models/controlnet" --out "controlnet-canny-scribble-integrated-sdxl-v2-fp16.safetensors" "https://huggingface.co/r3gm/controlnet-canny-scribble-integrated-sdxl-v2-fp16/resolve/main/diffusion_pytorch_model.fp16.safetensors?download=true"




FROM alpine/git:2.36.2 AS custom_nodes

WORKDIR /custom_nodes

RUN git clone https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git && \
    cd ComfyUI_Custom_Nodes_AlekPet && \
    git checkout 30f3a39c6e6e5a164554d5fc6d5d6aa9f4ffb57c

RUN git clone https://github.com/yolain/ComfyUI-Easy-Use.git && \
    cd ComfyUI-Easy-Use && \
    git checkout d4a443607f39c7343bda0911324adcde58dd54cf

RUN git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git && \
    cd comfyui_controlnet_aux && \
    git checkout 4cd233c5d7afe2e51bf57ee7a5ba7e6fcb9cbb22


FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-lite-v5

# 内置自定义节点
RUN --mount=type=bind,from=custom_nodes,source=/custom_nodes,target=/custom_nodes \
    mkdir -p ${BUILTIN}/custom_nodes && \
    rsync -a --ignore-existing /custom_nodes/* ${BUILTIN}/custom_nodes

# 将 venv 指回到容器内
RUN grep -r "/venv" /venv/bin/* | awk -F: "{print \$1}" | xargs -I {} sed "s@${NAS_DIR}/venv@/venv@g" -i {}

# 更新依赖至最新
RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes -maxdepth 2 -type f -name requirements.txt | \
    xargs -I {} pip install -r {}

RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes/ComfyUI_Custom_Nodes_AlekPet -maxdepth 2 -type f -name requirements.txt | \
    xargs -I {} pip install -r {}

RUN find -L ${VIRTUAL_NAS}/venv -type l -delete

# 内置模型
RUN --mount=type=bind,from=models,source=/models,target=/models \
    mkdir -p ${BUILTIN}/models/checkpoints ${BUILTIN}/models/loras && \
    rsync -a --ignore-existing /models/* ${BUILTIN}/models/

# RUN mkdir ${BUILTIN}/models/yolo && \
#     cd ${BUILTIN}/models/yolo && \
#     ln -s ../ultralytics/bbox/* .

# 翻译插件
RUN argospm install translate-zh_en && \
    mkdir -p ${VIRTUAL_NAS}/root/.local/share/argos-translate && \
    rsync -a --ignore-existing /root/.local/share/argos-translate/ ${VIRTUAL_NAS}/root/.local/share/argos-translate/


ARG IMAGE_TAG=${IMAGE_TAG}
ENV IMAGE_TAG=${IMAGE_TAG}
RUN --mount=type=bind,source=/base/v5,target=/docker \
    mkdir -p ${COMFYUI}/models/configs && \
    bash /docker/init.bash

