package store

// Store KV 数据存储
type Store interface {
	// Save 存储 value 到 key
	Save(key string, value string) error
	// Load 从 key 加载 value
	Load(key string) (string, error)
}
