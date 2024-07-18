ARG BASE_IMAGE

FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-clay-v1

ARG IMAGE_TAG=${IMAGE_TAG}
ENV IMAGE_TAG=${IMAGE_TAG}
RUN --mount=type=bind,from=registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-lite-v3,source=/agent,target=/mnt/agent \
    --mount=type=bind,source=/base/v3,target=/docker \
    mkdir -p ${COMFYUI}/models/configs && \
    bash /docker/init.bash

