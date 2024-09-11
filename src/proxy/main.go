package main

import (
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"
)

func main() {
	port := os.Getenv("FC_LISTEN_PORT")
	if port == "" {
		port = "9000"
	}

	comfyUIHost := os.Getenv("COMFYUI_HOST")
	comfyUIHost = strings.TrimPrefix(comfyUIHost, "http://")
	comfyUIHost = strings.TrimPrefix(comfyUIHost, "https://")
	comfyUIHost = strings.Trim(comfyUIHost, "/")

	u, _ := url.Parse(fmt.Sprintf("http://%s", comfyUIHost))
	fmt.Printf("proxy to %s\n", u)

	proxy := httputil.NewSingleHostReverseProxy(u)
	proxy.Director = func(req *http.Request) {
		// HOST 处理
		req.URL.Scheme = "http"
		req.URL.Host = comfyUIHost
		req.Host = comfyUIHost

		// 保持 RequestID 一致，方便问题排查
		req.Header.Set("X-Fc-Trace-Id", req.Header.Get("X-Fc-Request-Id"))

		fmt.Printf("proxy %s\n", req.URL)
	}
	proxy.ModifyResponse = func(w *http.Response) error {
		// 处理重复的 Access-Control-Allow-Origin
		allowOrigin := w.Header.Values("Access-Control-Allow-Origin")
		if len(allowOrigin) > 0 {
			for _, origin := range allowOrigin {
				if origin != "*" {
					w.Header.Set("Access-Control-Allow-Origin", origin)
					break
				}
			}
		}

		// HTTP 触发器禁止通过 Web 访问，转发时需要去除对应的 Header
		w.Header.Set("Content-Disposition", "inline")

		return nil
	}

	fmt.Println("server start")
	err := http.ListenAndServe(fmt.Sprintf("0.0.0.0:%s", port), proxy)
	if err != nil {
		panic(err)
	}
}
