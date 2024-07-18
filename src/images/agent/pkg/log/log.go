package log

import (
	"fmt"
	"log"
	"os"

	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/config"
)

const (
	logPrefix = log.Ldate | log.Ltime | log.Lmicroseconds
)

var (
	debugLogger    = log.New(os.Stdout, "\033[1;33m[ DEBUG ] \033[0m ", logPrefix)
	infoLogger     = log.New(os.Stdout, "\033[1;34m[ INFO  ] \033[0m ", logPrefix)
	errorLogger    = log.New(os.Stderr, "\033[1;31m[ ERROR ] \033[0m ", logPrefix)
	watchDogLogger = log.New(os.Stderr, "\033[1;35m[ComfyUI] \033[0m ", logPrefix)
)

func Debugf(format string, a ...any) string {
	if config.Debug {
		msg := fmt.Sprintf(format, a...)
		debugLogger.Println(msg)
		return msg
	}

	return ""
}

func Infof(format string, a ...any) string {
	msg := fmt.Sprintf(format, a...)
	infoLogger.Println(msg)
	return msg
}

func Errorf(format string, a ...any) string {
	msg := fmt.Sprintf(format, a...)
	errorLogger.Println(msg)
	return msg
}

func WatchDog(msg string) {
	watchDogLogger.Println(msg)
}
