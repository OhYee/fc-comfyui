ARG BASE_IMAGE

FROM python:3.10.9-slim AS models

RUN apt update && apt install -y aria2

# https://civitai.com/models/209978/ice-style-xl
RUN aria2c -x 16 --dir "/models/loras" --out "ice.safetensors" "https://civitai.com/api/download/models/236506?type=Model&format=SafeTensor"


FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-clay-v2

# 内置模型
RUN --mount=type=bind,from=models,source=/models,target=/models \
    mkdir -p ${BUILTIN}/models/checkpoints ${BUILTIN}/models/loras && \
    rsync -a --ignore-existing /models/* ${BUILTIN}/models/

ARG IMAGE_TAG=${IMAGE_TAG}
ENV IMAGE_TAG=${IMAGE_TAG}
RUN --mount=type=bind,source=/base/v2,target=/docker \
    mkdir -p ${COMFYUI}/models/configs && \
    bash /docker/init.bash

