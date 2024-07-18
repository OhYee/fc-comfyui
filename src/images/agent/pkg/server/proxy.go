package server

import (
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"

	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/config"
)

var (
	// comfyuiProxy 转发请求到 ComfyUI
	comfyuiProxy = (func() *httputil.ReverseProxy {
		u, _ := url.Parse(fmt.Sprintf("http://%s", config.ComfyUIHost))
		proxy := httputil.NewSingleHostReverseProxy(u)
		proxy.ModifyResponse = func(w *http.Response) error {
			allowOrigin := w.Header.Values("Access-Control-Allow-Origin")
			if len(allowOrigin) > 0 {
				for _, origin := range allowOrigin {
					if origin != "*" {
						w.Header.Set("Access-Control-Allow-Origin", origin)
						break
					}
				}
			}

			return nil
		}
		return proxy
	})()
)

func Proxy(w http.ResponseWriter, r *http.Request) {
	comfyuiProxy.ServeHTTP(w, r)
}
