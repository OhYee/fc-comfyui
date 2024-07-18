package comfyui

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/config"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/log"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/utils"
)

// Prompt ComfyUI 出图请求
func Prompt(clientID string, prompt *TPrompt) (string, error) {
	res := new(TPromptResponse)

	_, err := utils.HttpPost(fmt.Sprintf("http://%s/prompt", config.ComfyUIHost), map[string]any{
		"client_id": clientID,
		"prompt":    prompt,
	}, res)
	if err != nil {
		return "", err
	}

	return res.PromptID, nil
}

// Progress ComfyUI 出图进度
func Progress(clientID string, callback func(msg *TWebsocketMessage) (close bool)) error {
	conn, _, err := websocket.DefaultDialer.Dial(fmt.Sprintf("ws://%s/ws?clientId=%s", config.ComfyUIHost, clientID), nil)
	if err != nil {
		return err
	}
	defer conn.Close()

	log.Debugf("client connected %s", clientID)
	defer log.Debugf("client disconnected %s", clientID)

	ctx := context.Background()
	cctx, cancel := context.WithCancel(ctx)
	defer cancel()

	for {
		select {
		case <-cctx.Done():
			log.Debugf("progress websocket closed due to context canceled")
			break
		default:
			// msg 不能被共享，否则可能会使用上一次的值作为默认值
			msg := new(TWebsocketMessage)
			// err = conn.ReadJSON(msg)

			_, p, err := conn.ReadMessage()
			if err != nil {
				log.Errorf("read message error, %s", err)
				return err
			}

			log.Debugf("got message from client %s, %s", clientID, p)

			if err := json.Unmarshal(p, msg); err != nil {
				log.Errorf("unmarshal message error, %s", err)
				return err
			}

			// 再检查一次状态
			select {
			case <-cctx.Done():
				break
			default:
			}

			if callback(msg) {
				log.Debugf("client %s prompt %s close", clientID, msg.Data.PromptID)
				cancel()
				return nil
			}
		}
	}
}

func UploadImage(image []byte, overwrite bool) (*TWebsocketMessageOutputImage, error) {

	body := new(bytes.Buffer)
	writer := multipart.NewWriter(body)

	if overwrite {
		overwriteField, err := writer.CreateFormField("overwrite")
		if err != nil {
			return nil, fmt.Errorf("set overwrite field failed, %s", err)
		}
		n, err := overwriteField.Write([]byte("1"))
		if err != nil {
			return nil, fmt.Errorf("set overwrite field failed, %s", err)
		}
		if n == 0 {
			return nil, fmt.Errorf("set overwrite field failed, write 0 bytes")
		}
	}

	filename := uuid.NewString()
	part, err := writer.CreateFormFile("image", filename)
	if err != nil {
		return nil, fmt.Errorf("set image field failed, %s", err)
	}

	for {
		n, err := part.Write(image)
		if err != nil {
			log.Errorf("upload image failed, %s", err)
			break
		}
		if n == 0 {
			break
		}
		image = image[n:]
	}

	if err = writer.Close(); err != nil {
		return nil, fmt.Errorf("upload image failed due to close fileform error, %s", err)
	}

	uploadResp, err := http.Post(fmt.Sprintf("http://%s/upload/image", config.ComfyUIHost), writer.FormDataContentType(), body)
	if err != nil {
		return nil, fmt.Errorf("upload image failed due to http error, %s", err)
	}
	defer uploadResp.Body.Close()

	b, err := io.ReadAll(uploadResp.Body)
	if err != nil {
		return nil, fmt.Errorf("upload image read response error, %s", err)
	}

	output := new(TWebsocketMessageOutputImage)
	if err = json.Unmarshal(b, output); err != nil {
		return nil, fmt.Errorf("parse upload image body to json error, %s", err)
	}

	return output, nil
}
