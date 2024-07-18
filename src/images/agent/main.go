/*
转发所有请求到 comfyui 程序中
*/
package main

import (
	"fmt"
	"net/http"
	"os"

	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/config"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/log"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/server"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/watchdog"
)

type handler struct{}

// ServeHTTP HTTP 请求处理函数
func (h *handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	server.Router(w, r)
}

func main() {
	// 先拉起 ComfyUI
	wd := watchdog.New(config.ComfyUIPort, os.Args[1:])
	err := wd.Start()
	if err != nil {
		log.Errorf("start comfyui failed, due to %s", err)
		return
	}

	// 再监听当前 agent 的端口
	http.ListenAndServe(fmt.Sprintf("0.0.0.0:%d", config.Port), &handler{})
}
