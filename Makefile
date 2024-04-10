
.PHONY: help
help: ## 帮助文件
	@awk 'BEGIN {FS = ":.*?## "} /^[\.0-9a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


.PHONY: all
all: push ## 构建并推送镜像


.PHONY: clean
clean: 
	rm -rf .cache nas
	
NAMESPACE=ohyee
REPO=fc-demo

LITE_VERSION=fc-comfyui-lite-v1
SD1.5_VERSION=fc-comfyui-sd1.5-v1


##################
##   镜像构建   ##
##################

.PHONY: _build_docker
_build_docker:
	@DOCKER_BUILDKIT=1 docker build -f images/Dockerfile --target ${IMAGE_TARGET} -t ${IMAGE_REPO}:${IMAGE_VERSION} --build-arg IMAGE_TAG=${IMAGE_VERSION} images && \
	mkdir -p .cache && \
	docker inspect ${IMAGE_REPO}:${IMAGE_VERSION} -f '{{.Created}}' | xargs -I {} date -d {} '+%Y%m%d%H%M.%S' | xargs -I {} touch -t {} .cache/docker.image.comfyui.${IMAGE_TARGET}.timestamp	

.cache/docker.image.comfyui.lite.timestamp: ${shell find images -type f -name "*" }
	@IMAGE_TARGET="lite" IMAGE_REPO="${REPO}" IMAGE_VERSION="${LITE_VERSION}" make _build_docker

.cache/docker.image.comfyui.sd1.5.timestamp: ${shell find images -type f -name "*" }
	@IMAGE_TARGET="sd1.5" IMAGE_REPO="${REPO}" IMAGE_VERSION="${SD1.5_VERSION}" make _build_docker

.PHONY: _image
_image:
	@IMAGE_TS="${shell docker inspect $${IMAGE_NAME_CHECK} -f '{{.Created}}' | xargs -I {} date -d {} +%s}" \
	FILE_TS="${shell stat $${IMAGE_FILE_CHECK} | awk '/Modify/ {for(i=2;i<=NF;i=i+1)printf "%s ", $$i;}' | xargs -I {} date -d {} +%s}" && \
	if [ "$${IMAGE_TS:-0}" -lt "$${FILE_TS}" ]; then \
		echo -e "build image \nImage:\t\t$$(date -d "@$${IMAGE_TS:-0}" '+%Y-%m-%d %H:%M:%S')\nDockerfile:\t$$(date -d "@$${FILE_TS:-0}" '+%Y-%m-%d %H:%M:%S')\n\n"; \
		sh -c "${BUILD_COMMAND}"; \
	else \
		echo "skip build image"; \
	fi

.PHONY: build-lite
build-lite: .cache/docker.image.comfyui.lite.timestamp ## 构建 lite 镜像  

.PHONY: build-sd1.5
build-sd1.5: .cache/docker.image.comfyui.sd1.5.timestamp ## 构建 sd1.5 镜像
	
.PHONY: build
build: build-lite build-sd1.5 # 构建全部镜像


################
#   镜像推送   #
################

REGIONS=cn-hangzhou cn-shanghai
TAGS=${LITE_VERSION} ${SD1.5_VERSION}

define PUSH_REGION
push-$(1): build
	@for tag in $(TAGS); do \
		echo "\npush image \033[2m registry.$(1).aliyuncs.com/$(NAMESPACE)/$(REPO):$$$${tag} \033[0m \n" && \
		docker tag $(REPO):$$$${tag} registry.$(1).aliyuncs.com/$(NAMESPACE)/$(REPO):$$$${tag} && \
		docker push registry.$(1).aliyuncs.com/$(NAMESPACE)/$(REPO):$$$${tag} || exit 1 ; \
	done
endef

# 定义一个变量，包含所有 push-<region> 目标的名称
PUSH_TARGETS := $(foreach region,$(REGIONS),push-$(region))

.PHONY: $(PUSH_TARGETS)
$(foreach region,$(REGIONS),$(eval $(call PUSH_REGION,$(region))))

.PHONY: push build $(PUSH_TARGETS)
push: $(PUSH_TARGETS) ## 推送镜像到所有支持的地区


#################
##   模板发布  ##
#################
.PHONY: registry
registry: ## 发布到 Serverless Devs Registry
	s registry publish


##################
##   本地测试   ##
##################

.PHONY: dev
dev: build-sd1.5  ## 使用 sd1.5 进行测试
	docker run --rm -it --gpus=all --name=comfyui --net=host \
		-v ${shell pwd}/nas:/mnt/auto \
		${REPO}:${SD1.5_VERSION}

.PHONY: dev-lite
dev-lite: build-lite  ## 使用 lite 进行测试
	docker run --rm -it --gpus=all --name=comfyui --net=host \
		-v ${shell pwd}/nas:/mnt/auto \
		${REPO}:${LITE_VERSION}

.PHONY: dev-without-nas
dev-without-nas: build-sd1.5  ## 使用 sd1.5 进行测试，不挂载 nas
	docker run --rm -it --gpus=all --name=comfyui --net=host \
		${REPO}:${SD1.5_VERSION}

.PHONY: shell
shell: build-sd1.5  ## 登入 comfyui shell 环境
	docker run --rm -it --name=comfyui --net=host \
		--entrypoint="" \
		-v ${shell pwd}/nas:/mnt/auto \
		${REPO}:${SD1.5_VERSION} /bin/bash

.PHONY: exec
exec: ## 登入容器实例
	docker exec -it comfyui /bin/bash

