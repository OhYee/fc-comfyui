import io
import tarfile
import pytest
import os
import shutil
from datetime import datetime
from services.workspace.snapshot_manager import SnapshotManager
import constants


@pytest.fixture
def setup_snapshot_files(tmp_path):
    # 创建快照目录结构
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()

    # 创建多个快照目录
    snapshots = [
        "20231201-120000",
        "20231202-115959",
        "20231202-120000"
    ]

    for snapshot in snapshots:
        snapshot_path = snapshot_dir / snapshot
        snapshot_path.mkdir()

        # 创建comfyui目录和测试文件
        (snapshot_path / "comfyui").mkdir()
        (snapshot_path / "comfyui/test.txt").write_text("test content")

        # 创建venv.tar文件
        tar_path = snapshot_path / "venv.tar"
        with tarfile.open(tar_path, "w") as tar:
            test_content = "This is a test file in venv"
            test_file = io.BytesIO(test_content.encode())
            tarinfo = tarfile.TarInfo(name="venv/test_venv.txt")
            tarinfo.size = len(test_content)
            tar.addfile(tarinfo, test_file)

    # 创建挂载目录和模型目录
    mnt_dir = tmp_path / "mnt"
    mnt_dir.mkdir()
    models_dir = mnt_dir / "models"
    models_dir.mkdir()
    (models_dir / "test_model.bin").write_text("test model content")

    # 设置常量
    constants.SNAPSHOT_DIR = str(snapshot_dir)
    constants.WORK_DIR = str(tmp_path / "work")
    constants.MNT_DIR = str(mnt_dir)
    constants.COMFYUI_DIR = str(tmp_path / "work/comfyui")

    os.makedirs(constants.WORK_DIR, exist_ok=True)

    return tmp_path


def test_load_latest_snapshot(setup_snapshot_files):
    manager = SnapshotManager()
    snapshot_name = manager.load(SnapshotManager.USE_LATEST)

    assert snapshot_name == "20231202-120000"
    assert manager.cur_snapshot_name == "20231202-120000"

    # 验证文件复制和解压
    assert os.path.exists(os.path.join(constants.WORK_DIR, "comfyui/test.txt"))
    assert os.path.exists(os.path.join(constants.WORK_DIR, "venv/test_venv.txt"))
    assert not os.path.exists(os.path.join(constants.WORK_DIR, "venv.tar"))

    # 验证模型目录软链接
    models_link = os.path.join(constants.COMFYUI_DIR, "models")
    assert os.path.islink(models_link)
    assert os.readlink(models_link) == os.path.join(constants.MNT_DIR, "models")
    assert os.path.exists(os.path.join(models_link, "test_model.bin"))


def test_load_specific_snapshot(setup_snapshot_files):
    manager = SnapshotManager()
    snapshot_name = manager.load("20231202-115959")

    assert snapshot_name == "20231202-115959"
    assert manager.cur_snapshot_name == "20231202-115959"

    # 验证模型目录软链接
    models_link = os.path.join(constants.COMFYUI_DIR, "models")
    assert os.path.islink(models_link)
    assert os.readlink(models_link) == os.path.join(constants.MNT_DIR, "models")


def test_load_nonexistent_snapshot(setup_snapshot_files):
    manager = SnapshotManager()
    snapshot_name = manager.load("nonexistent")

    assert snapshot_name is None
    assert manager.cur_snapshot_name is None


def test_load_same_snapshot_twice(setup_snapshot_files):
    manager = SnapshotManager()
    first_load = manager.load("20231202-120000")
    second_load = manager.load("20231202-120000")

    assert first_load == second_load
    assert manager.cur_snapshot_name == "20231202-120000"

    # 验证模型目录软链接仍然存在且正确
    models_link = os.path.join(constants.COMFYUI_DIR, "models")
    assert os.path.islink(models_link)
    assert os.readlink(models_link) == os.path.join(constants.MNT_DIR, "models")


def test_select_latest_snapshot_with_invalid_format(setup_snapshot_files):
    invalid_snapshot = os.path.join(constants.SNAPSHOT_DIR, "invalid_format")
    os.makedirs(invalid_snapshot)

    manager = SnapshotManager()
    latest = manager._select_latest_snapshot()

    assert latest == "20231202-120000"


def test_select_latest_snapshot_empty_dir(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    constants.SNAPSHOT_DIR = str(empty_dir)

    manager = SnapshotManager()
    latest = manager._select_latest_snapshot()

    assert latest is None


def test_save_snapshot(setup_snapshot_files):
    # 准备要保存的文件
    comfyui_dir = os.path.join(constants.WORK_DIR, "comfyui")
    venv_dir = os.path.join(constants.WORK_DIR, "venv")
    os.makedirs(comfyui_dir)
    os.makedirs(venv_dir)

    test_file_comfyui = os.path.join(comfyui_dir, "test.txt")
    test_file_venv = os.path.join(venv_dir, "test.txt")

    with open(test_file_comfyui, 'w') as f:
        f.write("new comfyui content")
    with open(test_file_venv, 'w') as f:
        f.write("new venv content")

    # 执行保存
    manager = SnapshotManager()
    new_snapshot_name = manager.save()

    # 验证保存结果
    assert datetime.strptime(new_snapshot_name, constants.SNAPSHOT_PATTERN)
    new_snapshot_path = os.path.join(constants.SNAPSHOT_DIR, new_snapshot_name)

    assert os.path.exists(os.path.join(new_snapshot_path, "comfyui/test.txt"))
    assert os.path.exists(os.path.join(new_snapshot_path, "venv.tar"))

    # 验证文件内容
    with open(os.path.join(new_snapshot_path, "comfyui/test.txt"), 'r') as f:
        assert f.read() == "new comfyui content"


def test_load_after_save(setup_snapshot_files):
    # 准备要保存的文件
    comfyui_dir = os.path.join(constants.WORK_DIR, "comfyui")
    venv_dir = os.path.join(constants.WORK_DIR, "venv")
    os.makedirs(comfyui_dir)
    os.makedirs(venv_dir)

    test_file_comfyui = os.path.join(comfyui_dir, "test.txt")
    test_file_venv = os.path.join(venv_dir, "test.txt")

    with open(test_file_comfyui, 'w') as f:
        f.write("new comfyui content")
    with open(test_file_venv, 'w') as f:
        f.write("new venv content")

    # 保存新快照
    manager = SnapshotManager()
    saved_snapshot_name = manager.save()
    assert saved_snapshot_name == manager.cur_snapshot_name

    # 清理工作目录
    shutil.rmtree(comfyui_dir)
    shutil.rmtree(venv_dir)

    # 加载最新快照
    loaded_snapshot_name = manager.load(SnapshotManager.USE_LATEST)

    # 验证不会重新加载目录
    assert loaded_snapshot_name == saved_snapshot_name
    assert not os.path.exists(os.path.join(constants.WORK_DIR, "comfyui/test.txt"))


@pytest.fixture(autouse=True)
def cleanup(setup_snapshot_files):
    yield
    shutil.rmtree(setup_snapshot_files)
