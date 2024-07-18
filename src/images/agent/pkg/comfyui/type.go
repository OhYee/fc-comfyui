package comfyui

type TPromptNode struct {
	Inputs    map[string]any `json:"inputs"`
	ClassType string         `json:"class_type"`
	Meta      map[string]any `json:"_meta"`
}

type TPrompt map[string]TPromptNode

type TPromptResponse struct {
	PromptID string `json:"prompt_id"`
}

type TWebsocketMessage struct {
	// Type include `status`, `execution_start`, `execution_cached`, `executing`, `progress`, `executed`
	Type string                `json:"type"`
	Data TWebsocketMessageData `json:"data"`
}

type TWebsocketMessageData struct {
	SID      string                  `json:"sid"`
	PromptID string                  `json:"prompt_id"`
	Status   TWebsocketMessageStatus `json:"status"`
	Nodes    []string                `json:"nodes"`
	Node     string                  `json:"node"`
	Max      int                     `json:"max"`
	Value    int                     `json:"value"`
	Output   TWebsocketMessageOutput `json:"output"`
}

type TWebsocketMessageStatus struct {
	ExecInfo struct {
		QueueRemaining int `json:"queue_remaining"`
	}
}

type TWebsocketMessageOutput struct {
	Images []TWebsocketMessageOutputImage `json:"images"`
	Tags   []string                       `json:"tags"`
}

type TWebsocketMessageOutputImage struct {
	Filename  string `json:"filename"`
	Name      string `json:"Name"`
	SubFolder string `json:"subfolder"`
	// Type must be image
	Type string `json:"type"`
}
