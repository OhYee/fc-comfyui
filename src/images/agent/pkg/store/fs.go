package store

import (
	"io/fs"
	"os"
	"path"
)

// FS 基于文件系统进行存储
type FS struct {
	dir string
}

// NewFS 初始化文件系统存储
func NewFS(dir string) *FS {
	return &FS{dir: dir}
}

// Save ...
func (s *FS) Save(key string, value string) error {
	fp := path.Join(s.dir, key)

	os.MkdirAll(path.Dir(fp), 0644)
	return os.WriteFile(fp, []byte(value), fs.FileMode(os.O_WRONLY))
}

// Load ...
func (s *FS) Load(key string) (string, error) {
	b, err := os.ReadFile(path.Join(s.dir, key))
	if err != nil {
		return "", err
	}

	return string(b), nil
}
