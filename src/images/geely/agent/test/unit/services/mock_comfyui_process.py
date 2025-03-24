import signal
import time
import sys
import os
from flask import Flask
import threading
from werkzeug.serving import make_server

app = Flask(__name__)
server = None


class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', 8188, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


@app.route('/', methods=['GET'])
def hello():
    return "Flask server is running!"


def signal_handler(signum, frame):
    print(f"Received signal {signum}")
    if signum == signal.SIGTERM:
        print("Shutting down...")
        if server:
            server.shutdown()
        sys.exit(0)
    elif signum == signal.SIGHUP:
        print("Restarting server...")
        if server:
            server.shutdown()
        os.execv(sys.executable, ['python3'] + sys.argv)


def main():
    current_pid = os.getpid()
    print(f"Current process PID: {current_pid}")

    # 注册信号处理器
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    # 模拟启动过程
    print("Flask server starting...")
    counter = 0
    while counter < 3:
        print(f"Flask server boot log message #{counter}")
        counter += 1
        time.sleep(1)

    try:
        # 创建并启动服务器线程
        global server
        server = ServerThread(app)
        server.start()
        print("Server is listening on port 8188")

        # 主线程继续输出日志
        counter = 0
        while True:
            print(f"Flask server log message #{counter}")
            counter += 1
            time.sleep(1)

    except Exception as e:
        print(f"Failed to start server: {e}")
        if server:
            server.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
