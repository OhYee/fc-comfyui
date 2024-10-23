

FROM golang:1.21 AS agent

COPY agent /code
RUN cd /code
WORKDIR /code
RUN go get
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /agent main.go

ARG BASE_IMAGE

FROM registry.cn-hangzhou.aliyuncs.com/ohyee/fc-demo:fc-comfyui-board-v1

COPY --from=agent /agent /agent
