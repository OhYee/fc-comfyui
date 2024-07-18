package watchdog

import (
	"bufio"
	"bytes"
	"context"
	"fmt"
	"io"
	"net"
	"os/exec"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/config"
	"github.com/ohyee/fc-comfyui/src/images/agent/pkg/log"
)

// NewWatchDog 初始化一个监控程序，确保子程序被正确拉起
func New(port int, command []string) *WatchDog {
	w := &WatchDog{
		Port:    port,
		Command: command,
	}
	w.init()

	return w
}

// WatchDog 监控程序
type WatchDog struct {
	Port    int
	Command []string

	stdoutR io.Reader
	stdoutW io.Writer
	stderrR io.Reader
	stderrW io.Writer

	ctx    context.Context
	cancel context.CancelFunc

	waitGroup sync.WaitGroup

	hasCheckHealth bool
	isStarting     bool
}

func (w *WatchDog) init() {
	if w.ctx == nil {
		w.ctx, w.cancel = context.WithCancel(context.Background())
	}

	if w.stdoutR == nil || w.stdoutW == nil {
		w.stdoutR, w.stdoutW = io.Pipe()
	}

	if w.stderrR == nil || w.stderrW == nil {
		w.stderrR, w.stderrW = io.Pipe()
	}
}

// CheckPort 检查端口是否可用
func (w *WatchDog) CheckPort() bool {
	if w.Port == 0 {
		log.Errorf("watchdog port is not set")
		return false
	}

	conn, err := net.DialTimeout("tcp", fmt.Sprintf("localhost:%d", w.Port),
		time.Duration(100)*time.Millisecond)
	if err != nil {
		log.Debugf("check port error, %s", err)
		return false
	}
	defer conn.Close()

	return true
}

func (w *WatchDog) checkHealthLoop() {
	log.Debugf("start checkHealthLoop")
	defer log.Debugf("stop checkHealthLoop")

	if w.hasCheckHealth {
		log.Debugf("checkHealthLoop has started, skip")
		return
	}

	w.hasCheckHealth = true
	defer func() { w.hasCheckHealth = false }()

	w.waitGroup.Add(1)
	defer w.waitGroup.Done()

	ticker := time.NewTicker(time.Duration(config.WatchDogIntervalMs) * time.Microsecond)
	defer ticker.Stop()

	for {
		select {
		case <-w.ctx.Done():
			break

		case <-ticker.C:
			// 处于启动状态时，不进行端口检查
			if w.isStarting {
				continue
			}

			if !w.CheckPort() {
				retry := 5
				shouldRestart := true
				for retry > 0 {
					log.Debugf("port is not available, waiting...")
					retry--
					time.Sleep(time.Duration(config.WatchDogIntervalMs) * time.Millisecond)
					if w.CheckPort() {
						shouldRestart = false
						break
					}
				}

				if shouldRestart {
					log.Debugf("port is not available, try to restart")

					// 重试两次仍然未启动，重新拉起程序
					if err := w.Start(); err != nil {
						log.Errorf("WatchDog check health failed, and try to restart failed: %s", err)
						w.KillSelf()
					}
				}
			}
		}
	}
}

// Start 拉起程序并等待端口被监听
func (w *WatchDog) Start() error {
	log.Debugf("start watchdog")
	defer log.Debugf("start watchdog finished")

	if w.Command == nil || len(w.Command) == 0 {
		return fmt.Errorf("command is not set")
	}

	if w.isStarting {
		log.Infof("WatchDog is starting...")
		return nil
	}

	w.init()

	w.isStarting = true
	defer func() { w.isStarting = false }()

	log.Infof("command: %s", strings.Join(w.Command, " "))
	cmd := exec.CommandContext(w.ctx, w.Command[0], w.Command[1:]...)
	cmd.Stdout = w.stdoutW
	cmd.Stderr = w.stderrW

	err := cmd.Start()
	if err != nil {
		return err
	}

	go w.readOutputLoop(w.stdoutR)
	go w.readOutputLoop(w.stderrR)

	log.Infof("WatchDog is starting progress, waiting port available")

	// 等待端口启动
	for {
		time.Sleep(config.WatchDogIntervalMs * time.Millisecond)
		log.Debugf("pid %d, waiting port available...", cmd.Process.Pid)

		if w.CheckPort() {
			break
		}
	}

	log.Infof("port is available, start checkhealth")

	if !w.hasCheckHealth {
		go w.checkHealthLoop()
	}

	return nil
}

func (w *WatchDog) readOutputLoop(r io.Reader) {
	w.waitGroup.Add(1)
	defer w.waitGroup.Done()

	scanner := bufio.NewScanner(r)
	scanner.Split(func(data []byte, atEOF bool) (advance int, token []byte, err error) {
		if atEOF && len(data) == 0 {
			return 0, nil, nil
		}

		if i := bytes.IndexByte(data, '\n'); i >= 0 {
			return i + 1, (data[0:i]), nil
		}
		if atEOF {
			return len(data), (data), nil
		}
		return 0, nil, nil
	})

	for {
		select {
		case <-w.ctx.Done():
			return
		default:
			// buf := make([]byte, 102400)
			// n, err := r.Read(buf)
			if !scanner.Scan() {
				if err := scanner.Err(); err != nil {
					if w.isStarting {
						time.Sleep(config.WatchDogIntervalMs * time.Millisecond)
						continue
					}

					if err != io.EOF {
						log.Errorf("Scanner error: %s", err)
						continue
					}

					continue
				}

				continue
			}

			line := strings.TrimSpace(scanner.Text()) // 移除行首尾的空白字符
			if line != "" {
				log.WatchDog(line)
			}
		}
	}
}

// Stop 关闭所有线程
func (w *WatchDog) Stop() {
	log.Infof("WatchDog stop")
	w.cancel()
}

// WaitStop 等待关闭线程
func (w *WatchDog) WaitStop() {
	w.waitGroup.Wait()
}

// KillSelf 关闭所有线程，并 kill 当前进程
func (w *WatchDog) KillSelf() {
	w.Stop()
	w.WaitStop()

	log.Infof("WatchDog kill self")
	syscall.Kill(syscall.Getpid(), syscall.SIGTERM)
}
