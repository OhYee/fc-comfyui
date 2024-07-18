package store

import (
	"encoding/json"
)

// Progress 出图进度状态存储
type Progress struct {
	store Store
}

func NewProgress(store Store) *Progress {
	return &Progress{
		store: store,
	}
}

// SaveProgress 保存状态到存储
func (p *Progress) SaveProgress(key string, progress TProgress) error {
	return p.store.Save(key, progress.String())
}

// LoadProgress 从存储加载状态
func (p *Progress) LoadProgress(key string) (TProgress, error) {
	value, err := p.store.Load(key)
	if err != nil {
		return nil, err
	}

	res := make(TProgress)
	res.FromJSON(value)
	return res, nil
}

// TProgress 进度状态
type TProgress map[string]TProgressNode

// TProgressNode 节点状态
type TProgressNode struct {
	Max         int                  `json:"max"`
	Value       int                  `json:"value"`
	Start       int64                `json:"start"`
	LastUpdated int64                `json:"last_updated"`
	Images      []TProgressNodeImage `json:"images"`
	Results     []string             `json:"results,omitempty"`
}

type TProgressNodeImage struct {
	Filename  string `json:"filename"`
	SubFolder string `json:"subfolder"`
	// Type must be image
	Type string `json:"type"`
}

// String 转换 TProgress 到 JSON 字符串
func (p *TProgress) String() string {
	if p == nil {
		return ""
	}

	res, err := json.Marshal(p)
	if err != nil {
		return ""
	}

	return string(res)
}

func (p *TProgress) FromJSON(str string) {
	json.Unmarshal([]byte(str), p)
}
