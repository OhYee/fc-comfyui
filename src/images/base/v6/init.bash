#!/bin/bash

set -Eeuo pipefail

function mount_file_if_not_exist() {
  # 挂载单个文件到指定目录，如果已存在文件则不做处理
  SRC="$1"
  DST="$2"

  # 如果文件已经存在，则跳过
  if [ ! -e "${DST}" ]; then
    mkdir -p "$(dirname "${DST}")"
    ln -sT "${SRC}" "${DST}"
  fi 
}

function mount_folder_files() {
  # 挂载目录下直属的文件/文件夹到指定目录
  local SRC=$1
  local DST=$2
  ls ${SRC} | xargs -I {} bash -c "mount_file_if_not_exist ${SRC}/{} ${DST}/{}"
}

function mount_all_files() {
  # 挂载目录所有文件逐个到指定目录
  local SRC=$1
  local DST=$2
  find $SRC ! -type d -printf "%P\n" | xargs -I {} bash -c "mount_file_if_not_exist '${SRC}/{}' '${DST}/{}'"
}

function copy_file_if_not_exist() {
  # 复制文件到指定目录，如果已存在则跳过
  SRC="$1"
  DST="$2"

  if [ ! -e "$DST" ]; then
      mkdir -p $(dirname $DST)
      cp -r "$SRC" "$DST"
  fi
}

export -f mount_file_if_not_exist mount_folder_files copy_file_if_not_exist mount_all_files

 
# 处理 venv 虚拟环境

grep -r "/venv" /venv/bin/* | awk -F: "{print \$1}" | xargs -I {} sed "s@${NAS_DIR}/venv@/venv@g" -i {} # 先尝试将 venv 切回到默认位置

mount_file_if_not_exist /venv/bin ${VIRTUAL_NAS}/venv/bin
mount_file_if_not_exist /venv/include ${VIRTUAL_NAS}/venv/include
mount_file_if_not_exist /venv/pyvenv.cfg ${VIRTUAL_NAS}/venv/pyvenv.cfg
mount_file_if_not_exist /venv/include ${VIRTUAL_NAS}/venv/include
mount_folder_files /venv/lib/python3.10/site-packages ${VIRTUAL_NAS}/venv/lib/python3.10/site-packages
mount_folder_files /venv/lib64/python3.10/site-packages ${VIRTUAL_NAS}/venv/lib64/python3.10/site-packages
find -L ${VIRTUAL_NAS}/venv -type l -delete
export VIRTUAL_ENV="${NAS_DIR}/venv"
export PATH="${VIRTUAL_ENV}/bin:$PATH"
grep -r "/venv" /venv/bin/* | awk -F: '{print $1}' | xargs -I {} sed "s@/venv@${VIRTUAL_ENV}@" -i {}
echo "export VIRTUAL_ENV=${VIRTUAL_ENV}" >> /etc/profile
echo "export PATH=${PATH}" >> /etc/profile

mkdir -p ${VIRTUAL_NAS}/input ${VIRTUAL_NAS}/output ${VIRTUAL_NAS}/temp ${VIRTUAL_NAS}/custom_nodes

# 映射自定义节点 builtin => nas
mount_folder_files ${BUILTIN}/custom_nodes ${VIRTUAL_NAS}/custom_nodes
rm -rf ${COMFYUI}/custom_nodes

# 映射模型文件 builtin => nas
if [ -e "${COMFYUI}/models" ]; then
    rsync -a --ignore-existing ${COMFYUI}/models/* ${VIRTUAL_NAS}/models
    rm -rf ${COMFYUI}/models
fi

if [ -e ${BUILTIN}/models ]; then 
    mount_all_files "${BUILTIN}/models" "${VIRTUAL_NAS}/models"
fi

# 映射 input 文件 comfyui => nas builtin => nas
if [ -e "${COMFYUI}/input" ]; then mount_folder_files ${COMFYUI}/input ${VIRTUAL_NAS}/input; fi
if [ -e "${BUILTIN}/input" ]; then mount_folder_files ${BUILTIN}/input ${VIRTUAL_NAS}/input; fi

# 初始化额外模型文件 nas => comfyui
copy_file_if_not_exist "/docker/built-in/extra_model_paths.yaml" "${VIRTUAL_NAS}/extra_model_paths.yaml"


# 复制内置文件
cp /docker/entrypoint.bash /entrypoint.bash
chmod a+x /entrypoint.bash
if [ -f "/mnt/agent" ]; then
  if [ -f "/agent" ]; then rm /agent; fi
  cp /mnt/agent /agent
fi


# 写入镜像版本
IMAGE_TAG="${IMAGE_TAG:-$(date +%y%m%d%H%M%S)}" && echo "${IMAGE_TAG}" > /IMAGE_TAG