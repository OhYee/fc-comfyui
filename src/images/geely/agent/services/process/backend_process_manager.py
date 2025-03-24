import socket

import requests

import constants
from services.process.process_manager import ProcessManager


class BackendProcessManager(ProcessManager):
    # TODO: 进程重启问题
    def is_ready(self) -> bool:
        """
        检查进程是否就绪，通过检查对应端口是否已被监听来判断comfyui进程是否已启动完成

        Returns:
            bool: 如果进程已就绪则返回True，否则返回False
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', constants.BACKEND_PROCESS_PORT))
            sock.close()
            # TODO: 处理非预期result值
            return result == 0  # 若result为0，则端口被占用(即comfyui进程启动成功)
        except Exception:
            # TODO: handle corner cases
            return False

    def is_alive(self) -> bool:
        """
        通过发送 HTTP GET 请求到 ComfyUI 服务来检查进程是否存活

        Returns:
            bool: 如果在2秒内收到正常响应则返回True，否则返回False
        """
        try:
            response = requests.get(f'http://127.0.0.1:{constants.BACKEND_PROCESS_PORT}', timeout=2)
            return response.status_code == 200
        except Exception:
            # TODO: handle corner cases
            return False

