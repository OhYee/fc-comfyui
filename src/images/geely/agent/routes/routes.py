import logging
import threading
import traceback

import requests
import websocket
from flask import Flask, request, jsonify, Response
from flask_sock import Sock

import constants
from exceptions.exceptions import CustomError
from services.management_service import BackendStatus, ManagementService
from .management_routes import ManagementRoutes
from .serverless_api_routes import ServerlessApiRoutes


class Routes:
    def __init__(self):
        self.app = Flask(__name__)
        self._sock = Sock(self.app)
        self.setup_routes()

    def setup_routes(self):

        management = ManagementRoutes()
        management.register(self.app)
        
        serverless_api = ServerlessApiRoutes()
        serverless_api.register(self.app)

        @self.app.route("/initialize", methods=["POST"])
        def initialize():
            # See FC docs for all the HTTP headers: https://www.alibabacloud.com/help/doc-detail/132044.htm#common-headers
            request_id = request.headers.get("x-fc-request-id", "")
            print("FC Initialize Start RequestId: " + request_id)

            # Use the following code to get temporary credentials
            # access_key_id = request.headers['x-fc-access-key-id']
            # access_key_secret = request.headers['x-fc-access-key-secret']
            # access_security_token = request.headers['x-fc-security-token']

            # API模式需要自动启动comfyui进程
            # TODO 防止抛出5xx导致函数计算一直重试产生大量费用
            service = ManagementService()
            service.start(constants.AUTO_LAUNCH_SNAPSHOT_NAME)

            print("FC Initialize End RequestId: " + request_id)
            return "Function is initialized, request_id: " + request_id + "\n"

        @self._sock.route('/<path:path>')
        def proxy_ws(ws, path):
            backend_status = management.service.status
            if backend_status not in (BackendStatus.RUNNING, BackendStatus.SAVING):
                return jsonify({
                    "status": "failed",
                    "message": "Please start your comfyui/sd service first"
                }), 500

            # print(f"Forwarding websocket request for path: {path}")
            target_url = f"ws://{constants.APP_HOST}/{path}"

            def on_message(_, message):
                try:
                    ws.send(message)
                except Exception as ex:
                    logging.error(f"Error sending message to client: {ex}")

            def on_error(_, error):
                logging.error(f"WebSocket client error: {error}")

            def on_close(_, close_status_code, close_msg):
                logging.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")

            ws_client = websocket.WebSocketApp(
                target_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )

            ws_thread = threading.Thread(target=ws_client.run_forever)
            ws_thread.daemon = True
            ws_thread.start()

            try:
                while True:
                    message = ws.receive()
                    ws_client.send(message)
            finally:
                ws_client.close()

        @self.app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        @self.app.route("/", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
        def proxy(path=""):
            backend_status = management.service.status
            if backend_status not in (BackendStatus.RUNNING, BackendStatus.SAVING):
                return jsonify({
                    "status": "failed",
                    "message": "Please start your comfyui/sd service first"
                }), 500

            target_url = f"http://{constants.APP_HOST}/{path}"

            resp = requests.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                params=request.args,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                verify=False  # 如果需要验证SSL证书，将其设置为True
            )

            # issue: 实际内容被requests库解码，若保留content-encoding，可能会导致客户端试图重复解码，导致浏览器渲染SD页面失败
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            response_headers = {}
            for name, value in resp.headers.items():
                if name.lower() not in excluded_headers:
                    response_headers[name] = value

            return Response(
                response=resp.content,
                status=resp.status_code,
                headers=response_headers
            )

        @self.app.errorhandler(Exception)
        def handle_all_errors(error):
            return _handle_exception(error)

        @self.app.errorhandler(CustomError)
        def handle_base_error(error):
            return _handle_exception(error)

        def _handle_exception(e):
            err_msg = traceback.format_exc()
            print(f"{str(e)}\nStacktrace:\n{err_msg}")

            if isinstance(e, CustomError):
                # 处理自定义异常
                return jsonify({
                    "status": "failed",
                    "message": str(e)
                }), e.code
            else:
                # 处理其他非预期的异常
                return jsonify({
                    "status": "failed",
                    "message": str(e)
                }), 500
