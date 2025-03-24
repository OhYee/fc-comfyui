import subprocess
import threading
import time
from abc import ABC, abstractmethod
from typing import Optional

import constants


class ProcessManager(ABC):
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.stdout_thread = None
        self.stderr_thread = None
        self.health_check_thread = None
        self.should_monitor = False
        self._lock = threading.Lock()

    def start(self, command: list) -> None:
        """
        启动子进程

        Args:
            command: 要执行的命令列表，例如 ['python', 'script.py']
        """
        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1  # 行缓冲
            )
            print(f"Started process with PID: {self.process.pid}")

            # 启动标准输出和标准错误的读取线程
            def read_output(pipe):
                for line in iter(pipe.readline, ''):
                    print(line.strip())
                pipe.close()
            self.stdout_thread = threading.Thread(
                target=read_output,
                args=(self.process.stdout,),
                daemon=True
            )
            self.stderr_thread = threading.Thread(
                target=read_output,
                args=(self.process.stderr,),
                daemon=True
            )

            self.stdout_thread.start()
            self.stderr_thread.start()
        except Exception as e:
            print(f"Failed to start process: {e}")
            raise

    def wait_until_ready(self,
                         poll_interval: float = constants.DEFAULT_READINESS_POLL_INTERVAL,
                         timeout: float = constants.DEFAULT_READINESS_TIMEOUT) -> None:
        """
        同步轮询等待进程就绪

        Args:
            poll_interval: 轮询间隔时间(秒)
            timeout: 超时时间(秒)

        Returns:
            bool: 是否成功就绪
        """
        start_time = time.time()

        while True:
            # 检查是否超时
            if time.time() - start_time > timeout:
                print(f"Process startup timed out after {timeout} seconds")
                raise RuntimeError(f"Process startup timed out")

            # 检查是否就绪
            if self.is_ready():
                print("Process is ready")
                # 进程就绪后启动liveness探针
                self.start_health_check()
                return

            # 等待指定的轮询间隔
            time.sleep(poll_interval)

    def _health_check(self, poll_interval: float = constants.DEFAULT_LIVENESS_POLL_INTERVAL):
        """健康检查线程函数"""
        while self.should_monitor:
            try:
                if not self.is_alive():
                    print("Process is not living, restarting health check...")
                    self._on_process_died()
                time.sleep(poll_interval)
            except Exception as e:
                print(f"Error in health check: {e}")
                raise

    def _on_process_died(self):
        """进程死亡时的回调处理"""
        with self._lock:
            if self.process is not None:
                print(f"Process (PID: {self.process.pid}) died unexpectedly")
                # TODO: 增加处理逻辑

    def start_health_check(self, poll_interval: float = constants.DEFAULT_LIVENESS_POLL_INTERVAL):
        """启动健康检查线程"""
        with self._lock:
            if self.health_check_thread is None or not self.health_check_thread.is_alive():
                self.should_monitor = True
                self.health_check_thread = threading.Thread(
                    target=self._health_check,
                    args=(poll_interval,),
                    daemon=True
                )
                self.health_check_thread.start()
                print("Health check thread started")

    def stop(self) -> None:
        """停止子进程"""
        # 首先停止健康检查
        self.should_monitor = False
        if self.health_check_thread and self.health_check_thread.is_alive():
            self.health_check_thread.join()

        with self._lock:
            if self.process is None:
                return

            try:
                self.process.kill()
                self.process.wait()

                if self.process.stdout:
                    self.process.stdout.close()
                if self.process.stderr:
                    self.process.stderr.close()

                if self.stdout_thread and self.stdout_thread.is_alive():
                    self.stdout_thread.join(timeout=1)
                if self.stderr_thread and self.stderr_thread.is_alive():
                    self.stderr_thread.join(timeout=1)

                self.process = None
                self.stdout_thread = None
                self.stderr_thread = None
                self.health_check_thread = None

                print("Process killed")
            except Exception as e:
                print(f"Error stopping process: {e}")
                raise

    @abstractmethod
    def is_ready(self) -> bool:
        """检查进程是否就绪"""
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        """检查进程是否存活"""
        pass
