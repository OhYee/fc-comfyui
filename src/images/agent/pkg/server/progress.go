package server

import (
	"net/http"

	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/config"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/log"
)

func Progress(w http.ResponseWriter, r *http.Request) {
	id := r.URL.Query().Get("id")
	progress, err := config.TaskStore.LoadProgress(id)
	if err != nil {
		log.Errorf("query progress got failed: %s", err)
		http.Error(w, errorWrapper(ErrLoadProgress, err).Error(), http.StatusNotFound)
		return
	}

	w.Write([]byte(progress.String()))
	return
}
