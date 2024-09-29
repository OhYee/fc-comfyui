FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-lite-v3 as lite

# 更新 ComfyUI 版本
RUN cd / && \
    rm -rf ${COMFYUI} && \
    git clone https://github.com/comfyanonymous/ComfyUI.git ${COMFYUI} && \
    cd ${COMFYUI} && \
    git checkout de17a9755ecb8419cb167fe8504791df5b07246f

# 处理文件关系
ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

RUN --mount=type=bind,source=/base/v3,target=/docker \
    bash /docker/init.bash


