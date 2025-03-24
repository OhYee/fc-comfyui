import os


class FileSystem:

    def __init__(self, output_folder: str):
        self.output_folder = output_folder

    def __file_path(self, key: str):
        return os.path.join(self.output_folder, key)

    def get(self, key: str) -> str:
        try:
            with open(self.__file_path(key), "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            if "No such file or directory" not in str(e):
                print(e)

            return ""

    def put(self, key: str, value: str):
        try:
            os.makedirs(self.output_folder, exist_ok=True)

            with open(self.__file_path(key), "w", encoding="utf-8") as f:
                f.write(value)
        except Exception as e:
            print(e)
