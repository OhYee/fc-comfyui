package server

import (
	"net/http"
)

// SetCORS 写入跨域处理
func SetCORS(w http.ResponseWriter, r *http.Request) {
	// CORS
	w.Header().Set("Access-Control-Allow-Origin", r.Header.Get("Origin"))
	w.Header().Set("Access-Control-Allow-Headers", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE")
	w.Header().Set("Access-Control-Allow-Credentials", "true")
	w.Header().Set("Access-Control-Allow-Origin", r.Header.Get("Origin"))
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}
}

func Router(w http.ResponseWriter, r *http.Request) {
	// 判断下是路径，如果是特定的路径，则进行特殊处理，否则转发给 ComfyUI
	switch r.URL.Path {
	case "/api/run":
		// 调用 pipeline
		SetCORS(w, r)
		RunComfyUI(w, r)

	case "/api/run/ws":
		// 调用 pipeline
		// SetCORS(w, r)
		RunComfyUIWebsocket(w, r)

	case "/api/status":
		// 获取进度
		SetCORS(w, r)
		Progress(w, r)

	default:
		// 默认转发给 comfyui
		Proxy(w, r)
	}
}
