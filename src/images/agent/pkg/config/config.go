package config

import (
	"fmt"
	"os"
	"strings"

	"github.com/google/uuid"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/store"
)

const (
	Port        = 9000
	ComfyUIPort = 9001
	ComfyUIRoot = "/comfyui"
	TaskDir     = "/mnt/auto/comfyui/tasks"

	WatchDogIntervalMs = 500
)

var (

	// 当前客户端的 id
	ClientID = (func() string { return uuid.New().String() })()

	// taskStore 任务状态的存储，可以考虑存储在 OTS、RDS 等产品，这里只实现了文件系统存储
	TaskStore = (func() *store.Progress { return store.NewProgress(store.NewFS(TaskDir)) })()

	Debug = (func() bool {
		switch strings.ToLower(os.Getenv("DEBUG")) {
		case "0", "false", "":
			return false
		default:
			return true
		}
	})()

	ComfyUIHost = fmt.Sprintf("127.0.0.1:%d", ComfyUIPort)
)
