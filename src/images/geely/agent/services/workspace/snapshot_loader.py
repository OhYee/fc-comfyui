from abc import ABC, abstractmethod
from utils import file_ops
import constants


class SnapshotLoader(ABC):
    def __init__(self, timer):
        self.timer = timer

    def load(self, snapshot_path: str):
        with self.timer("Clearing work dir"):
            self._clear()

        with self.timer(f"Downloading snapshot from {snapshot_path}"):
            self._download(snapshot_path)

        with self.timer("Extracting dependencies"):
            self._extract()

        self._create_symlinks()

    @abstractmethod
    def _clear(self):
        """清理工作目录"""
        pass

    @abstractmethod
    def _download(self, snapshot_path: str):
        """下载快照"""
        pass

    @abstractmethod
    def _extract(self):
        """解压依赖"""
        pass

    @abstractmethod
    def _create_symlinks(self):
        """创建相关目录软链接"""
        pass


class ComfyUISnapshotLoader(SnapshotLoader):
    def _clear(self):
        file_ops.remove(constants.COMFYUI_DIR)
        file_ops.remove(constants.VENV_DIR)

    def _download(self, snapshot_path: str):
        file_ops.copy(f"{snapshot_path}/comfyui", constants.COMFYUI_DIR)
        file_ops.copy(f"{snapshot_path}/venv.tar", f"{constants.WORK_DIR}/venv.tar")

    def _extract(self):
        file_ops.extract(f"{constants.WORK_DIR}/venv.tar")
        file_ops.remove(f"{constants.WORK_DIR}/venv.tar")

    def _create_symlinks(self):
        file_ops.create_symlink(
            source_path=f"{constants.MNT_DIR}/models",
            link_path=f"{constants.COMFYUI_DIR}/models",
            force=True
        )


class SDSnapshotLoader(SnapshotLoader):
    def _clear(self):
        file_ops.remove(constants.SD_DIR)
        file_ops.remove(constants.VENV_DIR)

    def _download(self, snapshot_path: str):
        file_ops.copy(f"{snapshot_path}/stable-diffusion-webui", constants.SD_DIR)
        file_ops.copy(f"{snapshot_path}/venv.tar", f"{constants.WORK_DIR}/venv.tar")
        file_ops.copy(f"{snapshot_path}/.cache", f"{constants.WORK_DIR}/.cache")

    def _extract(self):
        file_ops.extract(f"{constants.WORK_DIR}/venv.tar")
        file_ops.remove(f"{constants.WORK_DIR}/venv.tar")

    def _create_symlinks(self):
        file_ops.create_symlink(
            source_path=f"{constants.MNT_DIR}/models",
            link_path=f"{constants.SD_DIR}/models",
            force=True
        )
