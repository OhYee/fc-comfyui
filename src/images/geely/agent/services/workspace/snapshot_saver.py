from abc import ABC, abstractmethod
from utils import file_ops
import constants


class SnapshotSaver(ABC):
    def __init__(self, timer):
        self.timer = timer

    def save(self, snapshot_path: str):
        with self.timer("Compressing dependencies"):
            self._compress()

        with self.timer(f"Uploading snapshot to {snapshot_path}"):
            self._upload(snapshot_path)

    @abstractmethod
    def _compress(self):
        """打包"""
        pass

    @abstractmethod
    def _upload(self, snapshot_path: str):
        """上传"""
        pass


class ComfyUISnapshotSaver(SnapshotSaver):
    def _compress(self):
        file_ops.compress(f"{constants.WORK_DIR}/venv.tar", constants.WORK_DIR, ["venv"])

    def _upload(self, snapshot_path: str):
        file_ops.copy(constants.COMFYUI_DIR, f"{snapshot_path}/comfyui")
        file_ops.copy(f"{constants.WORK_DIR}/venv.tar", f"{snapshot_path}/venv.tar")


class SDSnapshotSaver(SnapshotSaver):
    def _compress(self):
        file_ops.compress(f"{constants.WORK_DIR}/venv.tar", constants.WORK_DIR, ["venv"])

    def _upload(self, snapshot_path: str):
        file_ops.copy(constants.SD_DIR, f"{snapshot_path}/stable-diffusion-webui")
        file_ops.copy(f"{constants.WORK_DIR}/venv.tar", f"{snapshot_path}/venv.tar")
        file_ops.copy(f"{constants.WORK_DIR}/.cache", f"{snapshot_path}/.cache")
