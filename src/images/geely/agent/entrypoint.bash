#!/bin/bash

# 文件目录总览
# - /root: 工作目录
# -- agent: agent程序所在目录
# -- comfyui
# --- models: comfyui模型目录，软链接到挂载存储中，/root/comfyui/models -> ${MNT_DIR}/models
# --- ...
# -- venv: 依赖目录

# - ${MNT_DIR}: 挂载目录，NAS or OSS
# -- models: 用户模型本体，/root/comfyui/models -> ${MNT_DIR}/models
# -- input: 输入内容，例如图片
# -- output: 输出内容，例如图片
# -- snapshots: 快照目录
# --- 20250101-015959
# ---- comfyui
# ---- venv.tar
# --- 20250102-120159
# ---- comfyui
# ---- venv.tar

MNT_DIR=${MODEL_ASSET_DIR:="/mnt/auto"}
echo "Mount dir: ${MNT_DIR}"
if [ ! -e "${MNT_DIR}/models" ] || [ ! -e "${MNT_DIR}/snapshots" ] || [ -z "$(find "${MNT_DIR}/snapshots" -type d -mindepth 1 2>/dev/null)" ]; then
  echo "Missing models and snapshots folders in your mount dir"
  # exit 1
  # FIXME: 以下逻辑服务于带comfyui/sd环境的完整镜像；当支持启动阶段从官方源拉取comfyui源码和模型后，将以下逻辑可换为exit 1
  if [ "${BACKEND_TYPE}" = "comfyui" ]; then
    cp -r ${COMFYUI_DIR}/models ${MNT_DIR}/models
    rm -rf ${COMFYUI_DIR}/models
    ln -sf ${MNT_DIR}/models ${COMFYUI_DIR}/models
    ln -sf ${BUILT_IN_DIR}/models/checkpoints/sd-v1-5-inpainting.ckpt ${COMFYUI_DIR}/models/checkpoints/sd-v1-5-inpainting.ckpt
    mkdir -p ${MNT_DIR}/snapshots
    mkdir -p ${MNT_DIR}/input
    mkdir -p ${MNT_DIR}/output
  else
    # SD-WebUI
    cp -r ${SD_DIR}/models ${MNT_DIR}/models
    rm -rf ${SD_DIR}/models
    ln -sf ${MNT_DIR}/models ${SD_DIR}/models
    ln -sf ${BUILT_IN_DIR}/models/checkpoints/sd-v1-5-inpainting.ckpt ${SD_DIR}/models/Stable-diffusion/sd-v1-5-inpainting.ckpt
    mkdir -p ${MNT_DIR}/snapshots
  fi
fi

source ${AGENT_DIR}/venv/bin/activate
echo "Using python venv, python path '$(which python)', pip path '$(which pip)'... "
python ${AGENT_DIR}/main.py