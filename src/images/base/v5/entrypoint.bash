#!/bin/bash

set -Eeuo pipefail

source /etc/profile

function set_start_time() {
  START_TIME=$(date '+%s.%N')
}

function show_cost_time() {
  echo "$START_TIME $(date '+%s.%N')" | awk "{printf \"$1, cost %f seconds\n\", \$2 - \$1}"
}

function mount_file_if_not_exist() {
  SRC="$1"
  DST="$2"
 
  mkdir -p "$(dirname "${DST}")"

  # 如果文件已经存在，则跳过
  if [ ! -e ${DST} ]; then
    ln -sT "${SRC}" "${DST}"
  fi 
}

function mount_builtin_files() {
  set_start_time

  rsync -a --ignore-existing ${VIRTUAL_NAS}/* ${NAS_DIR}

  mount_file_if_not_exist ${NAS_DIR}/custom_nodes ${COMFYUI}/custom_nodes
  mount_file_if_not_exist "${NAS_DIR}/extra_model_paths.yaml" "${COMFYUI}/extra_model_paths.yaml"
  mount_file_if_not_exist "${NAS_DIR}/models" "${COMFYUI}/models"

  mkdir -p "${NAS_DIR}/root"  "${NAS_DIR}/temp" 
  rm -rf /root /tmp
  mount_file_if_not_exist "${NAS_DIR}/root" "/root"
  mount_file_if_not_exist "${NAS_DIR}/temp" "/tmp"

  show_cost_time "mount built-in files"
}


# 内置模型准备
# 如果挂载了 NAS，软链接到 NAS 中
# 如果未挂载 NAS，则尝试直接将内置模型过载
NAS_MOUNTED=0
if [ -d "/mnt/auto" ]; then
  NAS_MOUNTED=1
fi

mkdir -p ${NAS_DIR}

if [ "$NAS_MOUNTED" == "0" ]; then
  echo "without NAS"
else
  echo "with NAS"

  IMAGE_TAG_I=$(cat /IMAGE_TAG)
  IMAGE_TAG_N=$(cat ${NAS_DIR}/IMAGE_TAG 2>/dev/null || echo '') 

  echo "IMAGE_TAG [[${IMAGE_TAG_I}]] [[${IMAGE_TAG_N}]]"

  if [ "${IMAGE_TAG_I}" != "${IMAGE_TAG_N}" ]; then 
    # 去除无用的软链接/空文件夹
    echo "remove unused links"

    set_start_time
    find -L ${NAS_DIR} -type l -delete
    find ${NAS_DIR} ! -wholename ${NAS_DIR} -type d -empty -delete
    show_cost_time "remove symbolic links"

    echo -n ${IMAGE_TAG_I} > ${NAS_DIR}/IMAGE_TAG
  fi  
fi

mount_builtin_files

CLI_ARGS="${CLI_ARGS:---listen 0.0.0.0 --port 9000 --input-directory ${NAS_DIR}/input --output-directory ${NAS_DIR}/output --temp-directory ${NAS_DIR}/output}"
EXTRA_ARGS="${EXTRA_ARGS:-}"

export ARGS="${CLI_ARGS} ${EXTRA_ARGS}"

echo "args: $ARGS"

export PYTHONPATH="${COMFYUI}:${PYTHONPATH:-}"

if [ -f "${NAS_DIR}/startup.sh" ]; then
  . ${NAS_DIR}/startup.sh
fi

cd ${NAS_DIR}

if [ -z "${USE_AGENT:-}" ]; then
  python3 ${COMFYUI}/main.py ${ARGS}
else
  /agent python3 ${COMFYUI}/main.py $(echo ${ARGS} | sed "s/--port 9000/--port 9001/g")
fi 

