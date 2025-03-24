from enum import Enum
from threading import Lock
from typing import Dict, Set

import constants
from exceptions.exceptions import StateTransitionError
from services.process.backend_process_manager import BackendProcessManager
from services.workspace.snapshot_manager import SnapshotManager


class BackendStatus(Enum):
    STOPPED = "Stopped"
    STARTING = "Starting"
    RUNNING = "Running"
    SAVING = "Saving"
    STOPPING = "Stopping"


def singleton(cls):
    _instances = {}

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    return get_instance


@singleton
class ManagementService:
    _VALID_TRANSITIONS: Dict[BackendStatus, Set[BackendStatus]] = {
        BackendStatus.STOPPED: {BackendStatus.STARTING},
        BackendStatus.STARTING: {BackendStatus.RUNNING, BackendStatus.STOPPED},
        BackendStatus.RUNNING: {BackendStatus.SAVING, BackendStatus.STOPPING},
        BackendStatus.SAVING: {BackendStatus.RUNNING},
        BackendStatus.STOPPING: {BackendStatus.STOPPED, BackendStatus.RUNNING}
    }

    def __init__(self):
        self._process_mgr = BackendProcessManager()
        self._snapshot_mgr = SnapshotManager()
        self._status = BackendStatus.STOPPED
        self._status_lock = Lock()

    def _transition_to(self, new_status: BackendStatus) -> None:
        with self._status_lock:
            if new_status not in self._VALID_TRANSITIONS[self._status]:
                raise StateTransitionError(self._status, new_status)
            self._status = new_status

    @property
    def status(self) -> BackendStatus:
        with self._status_lock:
            return self._status

    def start(self, snapshot_name: str):
        print(f"Starting backend process using snapshot '{snapshot_name}'...")
        self._transition_to(BackendStatus.STARTING)

        try:
            # self._snapshot_mgr.load(snapshot_name)
            self._process_mgr.start(constants.BOOT_CMD)
            self._process_mgr.wait_until_ready()
            self._transition_to(BackendStatus.RUNNING)
        except Exception:
            self._transition_to(BackendStatus.STOPPED)
            raise

    def save(self):
        print("Saving workspace...")
        self._transition_to(BackendStatus.SAVING)

        try:
            self._snapshot_mgr.save()
            self._transition_to(BackendStatus.RUNNING)
        except Exception:
            self._transition_to(BackendStatus.RUNNING)
            raise

    def stop(self):
        print("Stopping workspace...")
        self._transition_to(BackendStatus.STOPPING)

        try:
            self._process_mgr.stop()
            self._transition_to(BackendStatus.STOPPED)
        except Exception:
            self._transition_to(BackendStatus.RUNNING)
            raise

    def save_and_stop(self):
        print("Saving and Stopping workspace...")
        self.save()
        self.stop()

    def find_snapshots(self):
        return self._snapshot_mgr.find_valid_snapshots()
