import re
import os
import json
import base64
import random
import asyncio
import threading
from urllib.parse import urlparse
import requests
import websocket
from typing import Any

import constants
from store import Store, FileSystem, OSS

from uuid import uuid4


class ServerlessApiService:
    def __init__(self):
        self.endpoint = f"http://{constants.APP_HOST}"

        # OSS 存储，需要时，可以将生成的图片同步至 OSS 中
        self.oss_store = OSS(
            constants.OSS_BUCKET_DOMAIN,
            constants.ALIBABA_CLOUD_ACCESS_KEY_ID,
            constants.ALIBABA_CLOUD_ACCESS_KEY_SECRET,
            constants.ALIBABA_CLOUD_SECURITY_TOKEN,
            constants.OSS_KEY_PREFIX,
            constants.OSS_EXPIRES_IN_SECOND,
        )

        # 状态持久化
        # 在异步调用 Serverless API 时，可以通过将状态写至持久化存储来确保在多个实例同时出图时仍然可以正确获取状态
        #
        # 默认实现了基于共享存储的方式实现的状态持久化（需要正确挂载 NAS）
        # 也可以考虑复用上面的 oss_store，将图片和状态均存储至 OSS 中
        # 如 `self.store: Store = self.oss_store`
        #
        # 必要时，也可以参考对应代码实现基于 Redis、TableStore、MySQL 等方式的状态持久化
        self.store: Store = FileSystem(f"{constants.MNT_DIR}/output/serverless_api")

    def api_prompt(self, client_id: str, prompt: Any):
        """
        出图
        """
        req = {"client_id": client_id, "prompt": prompt}
        res = requests.post(
            os.path.join(self.endpoint, "prompt"),
            json=req,
        )

        if res.status_code != 200:
            print({"prompt request": req})
            raise Exception(
                f"ComfyUI prompt api failed with {res.status_code}: {res.text}"
            )

        return res.json()

    def api_websocket(self, client_id: str, on_message):
        endpoint = re.subn(r"^http", "ws", self.endpoint, count=1)[0]

        ws = websocket.WebSocketApp(
            f'{os.path.join(endpoint, "ws")}?clientId={client_id}',
            on_message=on_message,
            keep_running=True,
        )

        return ws

    def api_upload_image(self, content: bytes, overwrite: bool):
        uuid = str(uuid4())
        files = {
            "image": (uuid, content),
        }

        if overwrite:
            files["overwrite"] = bytes("1")

        res = requests.post(
            os.path.join(self.endpoint, "upload/image"),
            files=files,
        )

        return res.json()

    def api_get_history(self, prompt_id: str):
        return requests.get(os.path.join(self.endpoint, "history", prompt_id)).json()

    def api_view_image(self, filename: str, img_type: str, sub_folder: str):
        return requests.get(
            os.path.join(self.endpoint, "view"),
            params={
                "filename": filename,
                "type": img_type,
                "subfolder": sub_folder,
                "rand": random.random(),
            },
        ).content

    def parse_prompt(self, prompt: map):
        """
        预处理 prompt 的内容
        - 如果以 base64、url 形式传输的图片，自动完成上传行为
        """
        for key, value in prompt.items():
            if type(value) == dict and value.get("class_type") == "LoadImage":
                try:
                    image = value.get("inputs", {}).get("image", "")
                    content = ""

                    if image.startswith("http://") or image.startswith("https://"):
                        # 图片来源于 url
                        content = requests.get(image).content
                    elif image.startswith("oss://"):
                        # 图片来源于 oss
                        arr = image.split("/")
                        host = arr[2]
                        path = "/".join(arr[3:])
                        oss = OSS(
                            host, 
                            constants.ALIBABA_CLOUD_ACCESS_KEY_ID,
                            constants.ALIBABA_CLOUD_ACCESS_KEY_SECRET,
                            constants.ALIBABA_CLOUD_SECURITY_TOKEN,
                            "",
                            0 ,
                        )
                        content = oss.get(path)
                    elif len(image) > 64:
                        # 图像可能是 base64，尝试使用 base64 解析
                        content = base64.b64decode(image.strip())
                    if content:
                        res = self.api_upload_image(content, False)
                        prompt[key]["inputs"]["image"] = res["name"]

                except Exception as e:
                    print(e)
            if type(value) == dict and value.get("class_type") == "KSampler":
                if value.get("inputs", {}).get("seed") == -1:
                    prompt[key]["inputs"]["seed"] = random.randint(0, 4294967296)
        return prompt

    def get_history_result(self, prompt_id: str, output_base64=False, output_oss=False):
        # 出图结果数组
        results = []
        history = self.api_get_history(prompt_id)

        for node_id, output in history.get(prompt_id, {}).get("outputs", {}).items():
            images = output.get("images", [])
            for index, img in enumerate(images):
                filename = img.get("filename", "")
                img_type = img.get("type", "")
                sub_folder = img.get("subfolder", "")
                img_output = None
                oss_object_key = None
                oss_url = None

                if output_base64 or output_oss:
                    img_bytes = self.api_view_image(filename, img_type, sub_folder)

                    if output_base64:
                        img_output = base64.b64encode(img_bytes).decode("ascii")

                    if output_oss:
                        if not self.oss_store.ready():
                            print("oss client is not init")
                        else:
                            oss_filename = f"{str(uuid4())}.png"
                            self.oss_store.put(oss_filename, img_bytes)
                            oss_object_key = self.oss_store.object_key(oss_filename)
                            oss_url = self.oss_store.sign(oss_filename)

                results.append(
                    {
                        "node_id": node_id,
                        "index": index,
                        "filename": filename,
                        "img_type": img_type,
                        "sub_folder": sub_folder,
                        "image": img_output,
                        "oss_object_key": oss_object_key,
                        "oss_url": oss_url,
                    }
                )

        return {
            "type": "serverless_api",
            "data": {"prompt_id": prompt_id, "results": results},
        }

    def put_status_to_store(self, task_id: str, status: str):
        """
        同步状态至持久化存储

        Args:
            task_id: 任务 id
            status: 增量的状态信息
        """
        if task_id and self.store:
            try:
                value = self.store.get(task_id)
                self.store.put(task_id, f"{value}\n{status}")
            except Exception as e:
                print("put status to store failed, due to", e)
            finally:
                pass

    def get_status_from_store(self, task_id: str):
        if self.store:
            value = self.store.get(task_id)
            return [json.loads(line) for line in value.split("\n") if line]
        else:
            return []

    def run(
        self,
        prompt: map,
        output_base64=False,
        output_oss=False,
        callback=None,
        task_id: str = None,
    ):
        """
        Serverless API 的核心逻辑
        """

        # 解析请求中是否存在 base64、http url 形式的图片
        prompt = self.parse_prompt(prompt)

        client_id = str(uuid4())
        prompt_id = ""

        # 如果 task id 未指定，则使用 client id
        if not task_id:
            task_id = client_id

        def on_message(ws: websocket.WebSocket, message: str):
            try:
                msg = json.loads(message)

                msg_type = msg.get("type", "")
                node_id = msg.get("data", {}).get("node", "")
                # current_prompt_id = msg.get("data", {}).get("prompt_id", "")

                if callback and hasattr(callback, "__call__"):
                    callback(message)

                self.put_status_to_store(task_id, message)

                if msg_type == "executing":
                    # 节点执行
                    if not node_id:
                        # 当前正在执行的 node 为空，说明 prompt 执行结束了
                        ws.close()
                        pass
                elif msg_type == "execution_error":
                    # 执行出错
                    pass
                else:
                    # 其他不处理的类型，如 "execution_start", "status", "progress", "execution_cached", "executed"
                    pass

            except Exception as e:
                print(e)

        ws = self.api_websocket(client_id, on_message)
        ws_threading = threading.Thread(target=ws.run_forever)
        ws_threading.start()

        # 提交出图任务
        prompt_result = self.api_prompt(client_id, prompt)
        prompt_id = prompt_result.get("prompt_id", "")

        if not prompt_id:
            raise Exception("can not get prompt_id from ComfyUI")

        ws_threading.join()

        result = self.get_history_result(
            prompt_id, output_base64=output_base64, output_oss=output_oss
        )
        self.put_status_to_store(task_id, json.dumps(result))
        return result
