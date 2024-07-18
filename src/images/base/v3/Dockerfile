FROM golang:1.21 AS agent

COPY agent /code
RUN cd /code
WORKDIR /code
RUN go get
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /agent main.go

ARG BASE_IMAGE

FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-lite-v2 as lite

# 处理文件关系
ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

RUN --mount=type=bind,from=agent,source=/agent,target=/agent \
    --mount=type=bind,source=/base/v3,target=/docker \
    bash /docker/init.bash


FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-sd1.5-v2 as sd1.5

ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

RUN --mount=type=bind,from=agent,source=/agent,target=/mnt/agent \
    --mount=type=bind,source=/base/v3,target=/docker \
    bash /docker/init.bash