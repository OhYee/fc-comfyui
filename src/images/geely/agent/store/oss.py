import os
from urllib.parse import urlparse, urlunparse
import constants
import oss2


class OSS:

    def __init__(
        self,
        endpoint,
        access_key_id,
        access_key_secret,
        security_token="",
        output_folder="comfyui_serverless_api",
        expires_in_second: int = 0,
    ):
        self.oss_bucket = None
        self.oss_endpoint = endpoint
        self.bucket_name = ""
        self.oss_bucket_key_prefix = output_folder.strip("/ ")
        self.oss_expires = 0

        if not endpoint:
            return

        try:
            self.oss_expires = int(expires_in_second)
        except:
            print(f"oss expires {expires_in_second} is invalid number")
            pass

        arr = self.oss_endpoint.split(".")
        if not (
            len(arr) == 4
            and arr[1].startswith("oss-")
            and arr[2] == "aliyuncs"
            and arr[3] == "com"
        ):
            print(f"oss endpoint {self.oss_endpoint} is invalid")
            return

        self.bucket_name = arr[0].split("/")[-1] if "/" in arr[0] else arr[0]
        self.region = arr[1].removeprefix("oss-").removesuffix("-internal")

        self.oss_bucket = oss2.Bucket(
            (
                oss2.StsAuth(access_key_id, access_key_secret, security_token)
                if security_token
                else oss2.Auth(access_key_id, access_key_secret)
            ),
            ".".join(arr[1:]),
            self.bucket_name,
        )

    def __file_path(self, key: str):
        return os.path.join(self.oss_bucket_key_prefix, key)

    def ready(self):
        return self.oss_bucket is not None

    def get(self, key: str) -> str:
        if not self.ready():
            print("oss client is not init")
            return ""

        try:
            with self.oss_bucket.get_object(self.__file_path(key)) as f:
                return f.read()
        except Exception as e:
            if "No such file or directory" not in str(e):
                print(e)

            return ""

    def put(self, key: str, value: str):
        if not self.ready():
            print("oss client is not init")
            return

        try:
            self.oss_bucket.put_object(self.__file_path(key), value)
        except Exception as e:
            print(e)

    def sign(self, key: str, expires_in_second=None):
        """
        针对特定的数据进行签名，允许匿名访问
        """
        if not self.ready():
            raise Exception("oss client is not init")

        if expires_in_second is None:
            expires_in_second = self.oss_expires

        if expires_in_second > 0:
            u = self.oss_bucket.sign_url(
                "GET", self.__file_path(key), expires_in_second, slash_safe=True
            )

            # url can visit on interet
            parsed = urlparse(u)
            host_parts = parsed.hostname.split(".")

            if (constants.OSS_OUTPUT_DOMAIN):
                parsed = parsed._replace(netloc=constants.OSS_OUTPUT_DOMAIN)
                u = urlunparse(parsed)
            elif (
                len(host_parts) == 4
                and host_parts[2] == "aliyuncs"
                and host_parts[3] == "com"
                and host_parts[1].startswith("oss-")
                and host_parts[1].endswith("-internal")
            ):
                # 去掉 "-internal"
                host_parts[1] = host_parts[1].removesuffix("-internal")
                new_hostname = ".".join(host_parts)
                if parsed.port:  # 保留端口（如果有）
                    new_hostname += f":{parsed.port}"

                # 替换 netloc，重建 URL
                parsed = parsed._replace(netloc=new_hostname)
                u = urlunparse(parsed)

            return u

        raise Exception(
            "oss expires must greater than 0, current is {expires_in_second}"
        )

    def object_key(self, key: str):
        """
        返回 OSS 中存储的实际 object key
        """
        return self.__file_path(key)
