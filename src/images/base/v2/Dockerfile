ARG BASE_IMAGE

FROM ${BASE_IMAGE} as base

# 更新 ComfyUI 版本
RUN cd / && \
    rm -rf ${COMFYUI} && \
    git clone https://github.com/comfyanonymous/ComfyUI.git ${COMFYUI} && \
    cd ${COMFYUI} && \
    git checkout 2d4164271634476627aae31fbec251ca748a0ae0 && \
    rm -rf .git

RUN mkdir -p ${BUILTIN}/custom_nodes && \
    mv ${COMFYUI}/custom_nodes/* ${BUILTIN}/custom_nodes


FROM base as lite
# 处理文件关系
ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

RUN --mount=type=bind,source=/v1,target=/docker \
    bash /docker/init.bash


FROM base as sd1.5

# 内置插件(费用提醒插件)
RUN --mount=type=bind,source=/v2,target=/docker \
    cp -R /docker/built-in/custom_nodes/* ${BUILTIN}/custom_nodes/

ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

RUN --mount=type=bind,source=/v2,target=/docker \
    bash /docker/init.bash