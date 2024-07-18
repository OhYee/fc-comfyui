package server

import (
	"encoding/json"
	"errors"

	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/utils"
)

type ErrType string

const (
	ErrParams         ErrType = "RequestParamsError"
	ErrCallPrompt     ErrType = "CallComfyUIPromptError"
	ErrLoadProgress   ErrType = "LoadProgressError"
	ErrMarshalResult  ErrType = "MarshalResultError"
	ErrUpgrade        ErrType = "WebsocketUpgradeError"
	ErrWriteWebsocket ErrType = "WebsocketWriteError"
)

type ErrMsg struct {
	Message ErrType `json:"message"`
	Err     any     `json:"error"`
}

func (e ErrMsg) Error() string {
	b, _ := json.Marshal(e)
	return string(b)
}

func errorWrapper(errType ErrType, err error) error {
	errMsg := err.Error()

	httpError := new(utils.HTTPError)
	if hasHTTPError := errors.As(err, httpError); hasHTTPError {
		errMsg = httpError.Body
	}

	var errObj any = errMsg
	if errMsg[0] == '{' && errMsg[len(errMsg)-1] == '}' {
		errMapObj := new(map[string]any)
		if err := json.Unmarshal([]byte(errMsg), errMapObj); err == nil {
			errObj = errMapObj
		}
	} else if errMsg[0] == '[' && errMsg[len(errMsg)-1] == ']' {
		errArrObj := new([]any)
		if err := json.Unmarshal([]byte(errMsg), errArrObj); err == nil {
			errObj = errArrObj
		}
	}

	return ErrMsg{
		Message: errType,
		Err:     errObj,
	}
}
