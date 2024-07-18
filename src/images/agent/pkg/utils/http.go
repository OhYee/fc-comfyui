package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/log"
)

// HTTPError ...
type HTTPError struct {
	Status int    `json:"status"`
	Body   string `json:"body"`
}

func (e HTTPError) Error() string {
	return fmt.Sprintf("http error, status: %d, body: %s", e.Status, e.Body)
}

// ReadToJSON 读取二进制内容到 JSON 对象
func ReadToJSON(r io.Reader, target any) error {
	if target == nil {
		return nil
	}

	b, err := io.ReadAll(r)
	if err != nil {
		return err
	}

	err = json.Unmarshal(b, target)
	if err != nil {
		return err
	}

	return nil
}

func HttpGet(url string, target any) (*http.Response, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != 200 {
		b, _ := io.ReadAll(resp.Body)
		return resp, HTTPError{
			Status: resp.StatusCode,
			Body:   string(b),
		}
	}

	if err := ReadToJSON(resp.Body, target); err != nil {
		return resp, err
	}

	return resp, nil
}

func HttpPost(url string, body map[string]any, target any) (*http.Response, error) {
	bodyBytes, err := json.Marshal(body)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(url, "application/json", bytes.NewReader(bodyBytes))
	if err != nil {
		return nil, err
	}

	log.Debugf("%s", bodyBytes)

	if resp.StatusCode != 200 {
		b, _ := io.ReadAll(resp.Body)
		return resp, HTTPError{
			Status: resp.StatusCode,
			Body:   string(b),
		}
	}

	if err := ReadToJSON(resp.Body, target); err != nil {
		return resp, err
	}

	return resp, nil
}
