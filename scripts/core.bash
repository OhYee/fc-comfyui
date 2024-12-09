#!/bin/bash
# 自动识别 function cmd_xxx() { ## xxxxxxx 为可执行的命令，使用 xxx 进行执行
# 提供 debug、need_build、need_build_docker 辅助命令
set -e

_FILE=$(readlink -f "$0")
_DIR=$(dirname "$_FILE")
_COMMAND_PREFIX="cmd_"
_RETURN=""
_DEBUG_TRACE=""
_EXTRA_HELP=""


function add_help() { ## 增加一条帮助日志
    _EXTRA_HELP+="$1 $2\n" 
}

function cmd_help() { ## 显示帮助
    echo -e "帮助文档 \033[2m$0 $@\033[0m:"
    local tmp=""
    
    tmp+=$(awk 'BEGIN { FS="function cmd_|\\(\\)|{|## " } /^function cmd_/ {  printf "\033[36m%-40s\033[0m %s\n", $2, $5}' "$_FILE")
    tmp+="\n"
    tmp+=$(echo -e "$_EXTRA_HELP" | awk '{output=""; for(i=2;i<=NF;i++) output=output $i " "; printf "\033[36m%-40s\033[0m %s\n", $1, output}')
    echo -e "$tmp" | sort

}

function debug() { ## 测试日志
    local stack="${BASH_SOURCE[0]}:${BASH_LINENO[0]} ${FUNCNAME[1]}"
    if [ "${FUNCNAME[1]}" == "set_debug_trace" ] || [ "${FUNCNAME[1]}" == "clear_debug_trace" ]; then 
        stack="${BASH_SOURCE[0]}:${BASH_LINENO[1]} ${FUNCNAME[2]}"
    fi


    if [ -n "$DEBUG" ]; then
        if [ -n "$_DEBUG_TRACE" ]; then
            echo -en "\033[1;33m[$_DEBUG_TRACE]\033[0m " > /dev/stderr;
        fi

        echo -e "\033[33m${stack}\033[0m \033[2;33m"$@"\033[0m" > /dev/stderr;
    fi
}

function set_debug_trace() { ## 测试日志链路追踪
    local name=$(echo $1 | tr ' ' '_' | tr '/' '_')
    if [ -z "$name" ]; then
        name="${FUNCNAME[1]}"
    fi

    if [ -z "$_DEBUG_TRACE" ]; then
        _DEBUG_TRACE="$name"
    else
        _DEBUG_TRACE+="/$name"
    fi

    debug "start"
}

function clear_debug_trace() { ## 移除测试日志链路
    local key=$(echo "${_DEBUG_TRACE}" | sed 's@^.*/@@')
    debug "end"

    _DEBUG_TRACE=$(echo "${_DEBUG_TRACE}" | sed 's@/[^/]*$@@')
}

function need_build() { ## 根据文件日志检查是否需要进行构建
    set_debug_trace "need_build"

    if [ -n "$FORCE" ]; then
        debug "force build"
        echo "1"
        return
    fi

    # 定义函数来检查文件是否需要构建
    target_file="$1"
    shift
    source_files=("$@")
    
    debug "target file: $target_file"
    debug "source_files: $source_files"

    # 如果目标文件不存在，或者任何一个源文件的修改时间晚于目标文件，则需要重新构建
    if [[ ! -e "$target_file" ]]; then
        debug "target file $target_file not exist, should build"
        echo "1"
        return
    fi
    
    for source_file in "${source_files[@]}"; do
        if [[ "$source_file" -nt "$target_file" ]]; then
            debug "source file $target_file was modified, should build"
            echo "1"
            return
        fi
    done

    debug "no need to build"

    clear_debug_trace
}

function need_build_docker() { ## 根据 docker 镜像日期判断是否需要构建镜像
    set_debug_trace "need_build_docker"

    if [ -n "$FORCE" ]; then
        debug "force build"
        echo "1"
        return
    fi

    # 提取参数
    local image_name="$1"
    shift
    local source_files=("$@")

    debug "image name: $image_name"
    debug "source_files: $source_files"

    local image_ts="$(docker inspect ${image_name} -f '{{json .Metadata.LastTagTime}}' 2>/dev/null | xargs -I {} date -d {} +%s || 0)"
    if [ -z "$image_ts" ]; then image_ts="0"; fi
    debug "image_ts: ${image_ts}"

    for source_file in "${source_files[@]}"; do
        local file_ts="$(stat ${source_file} | awk '/Modify/ {for(i=2;i<=NF;i=i+1)printf "%s ", $i;}' | xargs -I {} date -d {} +%s)"
        debug "file__ts: ${file_ts} ${source_file}"

        if [ "${image_ts}" -lt "${file_ts}" ]; then \
            debug "source file $target_file was modified, should build"
            echo "1"
            return
        fi
    done

    debug "no need to build"

    clear_debug_trace
}

function init_help() {
    add_help "help" "显示帮助"
}

function main() {
    set_debug_trace

    init_help

    # 调用所有 init 函数
    for init in $(awk 'BEGIN { FS=" |\\(" } /^function init_.*\(\) *{ *$/ { print $2 }' $_FILE); do
        $init
    done

    local showHelp=1
    for c in $@; do
        cmd="${_COMMAND_PREFIX}${c}"
        
        if type "$cmd" &>/dev/null; then
            showHelp=""

            debug "run $c => $cmd"
            $cmd
        else
            echo "command $c not found, skip it."
        fi
    done

    if [ -n "$showHelp" ]; then
        cmd_help
    fi

    clear_debug_trace
}