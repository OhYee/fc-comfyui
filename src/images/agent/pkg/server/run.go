package server

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/comfyui"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/config"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/log"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/store"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/utils"
)

const (
	TASK_ID_HEADER = "task-id"
)

func readURLBytes(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("get remote image from %s error, %s", url, err)
	}
	defer resp.Body.Close()

	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("get remote image from %s error, %s", url, err)
	}

	return b, nil
}

func readBase64Bytes(b64 string) ([]byte, error) {
	return base64.StdEncoding.DecodeString(strings.TrimSpace(b64))
}

func parsePrompt(prompt *comfyui.TPrompt) {
	for key, value := range *prompt {
		if value.ClassType == "LoadImage" {
			image, exist := value.Inputs["image"]
			if !exist {
				continue
			}

			imageString, ok := image.(string)
			if !ok {
				continue
			}

			var imageBytes []byte
			var err error
			if strings.HasPrefix(imageString, "http://") || strings.HasPrefix(imageString, "https://") {
				imageBytes, err = readURLBytes(imageString)
				if err != nil {
					log.Errorf("%s", err)
					continue
				}
			} else if len(imageString) >= 64 {
				imageBytes, err = readBase64Bytes(imageString)
				if err != nil {
					log.Errorf("%s", err)
					continue
				}
			}

			file, err := comfyui.UploadImage(imageBytes, false)
			if err != nil {
				log.Errorf("upload image failed, %s", err)
				continue
			}

			inputs := value.Inputs
			inputs["image"] = file.Name
			value.Inputs = inputs
			(*prompt)[key] = value
		}
	}
}

func runComfyUI(clientID string, taskID string, prompt *comfyui.TPrompt, callback func(progress store.TProgress)) (store.TProgress, error) {
	parsePrompt(prompt)

	// 1. 调用出图接口
	promptID, err := comfyui.Prompt(clientID, prompt)
	if err != nil {
		log.Errorf("call prompt got error: %s", err)
		return nil, errorWrapper(ErrCallPrompt, err)
	}

	var logPrefix = fmt.Sprintf("[client %s] [task %s] [prompt %s]", clientID, taskID, promptID)
	log.Debugf("%s start to get progress", logPrefix)

	// 2. 建立 websocket 获取进度
	progress := make(store.TProgress)
	for nodeid := range *prompt {
		progress[nodeid] = store.TProgressNode{}
	}

	err = comfyui.Progress(clientID, func(msg *comfyui.TWebsocketMessage) (close bool) {
		log.Debugf("%s receive message %+v", logPrefix, msg)
		if msg == nil {
			log.Errorf("%s websocket msg is nil, ignore it", logPrefix)
			return false
		}

		// 非当前 prompt 的响应，忽略
		if msg.Data.PromptID != promptID {
			return false
		}

		defer func() {
			log.Debugf("%s callback progress %+v", logPrefix, progress)
			callback(progress)
		}()

		now := time.Now().Unix()
		nodeid := msg.Data.Node

		var promptNode comfyui.TPromptNode
		if prompt != nil {
			promptNode = (*prompt)[nodeid]
		}

		currentNodeProgress, exist := progress[nodeid]
		if !exist {
			if nodeid != "" {
				log.Infof("%s unknown node message %+v", logPrefix, msg)
			}
			currentNodeProgress = store.TProgressNode{}
			progress[nodeid] = currentNodeProgress
		}
		currentNodeProgress.LastUpdated = now

		defer func() {
			progress[nodeid] = currentNodeProgress
		}()

		switch msg.Type {
		case "status":
			break

		case "execution_cached":

		case "execution_start", "executing":
			// 当开始执行的 node 为空时，说明执行结束
			if nodeid == "" {
				log.Debugf("%s prompt finished", logPrefix)
				return true
			} else {
				log.Debugf("%s node %s start", logPrefix, nodeid)
				currentNodeProgress.Start = now
				if currentNodeProgress.Max == 0 {
					// 标记下当前 node 在执行状态
					currentNodeProgress.Max = 1
				}
			}
		case "execution_error", "executed":
			// 节点执行结束
			log.Debugf("%s node %s finished", logPrefix, nodeid)

			// 节点已完成时，修改下 Max 和 Value 至少为 1
			if currentNodeProgress.Max == 0 && currentNodeProgress.Value == 0 {
				currentNodeProgress.Max = 1
				currentNodeProgress.Value = 1
			}

			if promptNode.ClassType == "SaveImage" && msg.Data.Output.Images != nil && len(msg.Data.Output.Images) > 0 {
				// 如果是图片节点，则记录一下图片数据
				if currentNodeProgress.Images == nil {
					currentNodeProgress.Images = make([]store.TProgressNodeImage, 0, len(msg.Data.Output.Images))
				}

				for _, img := range msg.Data.Output.Images {
					currentNodeProgress.Images = append(currentNodeProgress.Images, store.TProgressNodeImage{
						Filename:  img.Filename,
						SubFolder: img.SubFolder,
						Type:      img.Type,
					})
				}
			}
		case "progress":
			log.Debugf("%s node %s progress %d/%d %d%%", logPrefix, nodeid, msg.Data.Value, msg.Data.Max, msg.Data.Value*100/msg.Data.Max)

			currentNodeProgress.Max = msg.Data.Max
			currentNodeProgress.Value = msg.Data.Value
		}

		return false
	})

	if err != nil {
		return progress, err
	}

	return progress, nil
}

func RunComfyUI(w http.ResponseWriter, r *http.Request) {
	taskID := r.Header.Get(TASK_ID_HEADER)
	if taskID == "" {
		taskID = uuid.NewString()
	}

	prompt := new(comfyui.TPrompt)
	err := utils.ReadToJSON(r.Body, prompt)
	if err != nil {
		log.Errorf("read request params error: %s", err)
		http.Error(w, errorWrapper(ErrParams, err).Error(), http.StatusInternalServerError)
		return
	}

	progress, err := runComfyUI(config.ClientID, taskID, prompt, func(progress store.TProgress) {
		if err := config.TaskStore.SaveProgress(taskID, progress); err != nil {
			log.Errorf("save task %s progress error: %s", taskID, err)
		}
	})
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	b, err := json.Marshal(progress)
	if err != nil {
		log.Errorf("marshal result error: %s", err)
		http.Error(w, errorWrapper(ErrMarshalResult, err).Error(), http.StatusInternalServerError)
		return
	}

	w.Write(b)
}

type websocketMessage struct {
	Type string `json:"type"`
	Data any    `json:"data"`
}

func RunComfyUIWebsocket(w http.ResponseWriter, r *http.Request) {
	taskID := r.Header.Get(TASK_ID_HEADER)
	if taskID == "" {
		taskID = uuid.NewString()
	}

	upgrader := websocket.Upgrader{}
	upgrader.CheckOrigin = func(r *http.Request) bool { return true }

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Errorf("upgrade websocket failed, %v", err)
		http.Error(w, errorWrapper(ErrUpgrade, err).Error(), http.StatusInternalServerError)
		return
	}
	defer conn.Close()

	prompt := new(comfyui.TPrompt)
	if err := conn.ReadJSON(prompt); err != nil {
		log.Errorf("parse prompt failed, %v", err)
		conn.WriteJSON(websocketMessage{
			Type: "error",
			Data: errorWrapper(ErrCallPrompt, err),
		})
		return
	}

	clientID := uuid.NewString()
	progress, err := runComfyUI(clientID, taskID, prompt, func(progress store.TProgress) {
		if err = conn.WriteJSON(websocketMessage{
			Type: "progress",
			Data: progress,
		}); err != nil {
			log.Errorf("websocket send progress failed, %s", err)
		}
	})
	if err != nil {
		conn.WriteJSON(websocketMessage{
			Type: "error",
			Data: err.Error(),
		})
		return
	}

	for i, p := range progress {
		if p.Images != nil && len(p.Images) > 0 {
			images := make([]string, 0, len(p.Images))
			for _, img := range p.Images {
				resp, err := http.Get(fmt.Sprintf("http://%s/view?filename=%s&type=%s&subfolder=%s&rand=%v", config.ComfyUIHost, img.Filename, img.Type, img.SubFolder, rand.Float64()))
				if err == nil {
					b, err := io.ReadAll(resp.Body)
					if err == nil {
						images = append(images, base64.RawStdEncoding.EncodeToString(b))
					} else {
						log.Errorf("read output image error, %s", err)
					}
				}
			}

			p.Results = images
			progress[i] = p
		}
	}

	if err := conn.WriteJSON(websocketMessage{
		Type: "result",
		Data: progress,
	}); err != nil {
		http.Error(w, errorWrapper(ErrWriteWebsocket, err).Error(), http.StatusInternalServerError)
		return
	}
}
