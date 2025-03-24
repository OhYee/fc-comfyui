import signal
import time
from pathlib import Path

import pytest

from services.process.backend_process_manager import BackendProcessManager


@pytest.fixture
def process_manager():
    return BackendProcessManager()


def test_start_real_process(process_manager):
    script_path = Path(__file__).parent / "mock_comfyui_process.py"

    # 启动进程
    command = ['python3', str(script_path)]
    process_manager.start(command)

    assert process_manager.process is not None
    assert process_manager.process.pid > 0
    assert process_manager.is_ready() is False  # 子进程Readiness探针未就绪

    # 等待子进程启动完成
    process_manager.wait_until_ready()

    # 等待正常运行N秒
    time.sleep(10)

    # 停止进程
    process_manager.stop()

    # 验证进程已终止
    time.sleep(1)
    assert process_manager.is_ready() is False


def test_process_manually_restart_on_unexpected_exit(process_manager):
    script_path = Path(__file__).parent / "mock_comfyui_process.py"

    # 首次启动进程
    command = ['python3', str(script_path)]
    process_manager.start(command)

    # 等待进程就绪
    process_manager.wait_until_ready()

    # 记录第一次启动的进程ID
    first_pid = process_manager.process.pid

    # 等待几秒确保进程稳定运行
    time.sleep(2)

    # 模拟进程意外退出（发送SIGTERM信号）
    process_manager.process.terminate()

    # 等待进程完全退出
    process_manager.process.wait()
    time.sleep(1)

    # 验证进程已经不再运行
    assert process_manager.is_ready() is False

    # 重新启动进程
    process_manager.start(command)

    # 等待新进程就绪
    process_manager.wait_until_ready()

    # 验证是新的进程（PID不同）
    assert process_manager.process.pid != first_pid

    # 最后停止进程
    process_manager.stop()

    # 验证进程已完全终止
    time.sleep(1)
    assert process_manager.is_ready() is False


def test_process_auto_restart_on_unexpected_exit(process_manager):
    script_path = Path(__file__).parent / "mock_comfyui_process.py"

    # 启动进程
    command = ['python3', str(script_path)]
    process_manager.start(command)

    # 等待进程就绪
    process_manager.wait_until_ready()

    # 记录第一次启动的进程ID
    first_pid = process_manager.process.pid

    # 等待几秒确保进程稳定运行和健康检查线程启动
    time.sleep(2)

    # 模拟进程意外退出（发送SIGTERM信号）
    process_manager.process.send_signal(signal.SIGHUP)

    # 等待足够长的时间，让健康检查线程检测到进程死亡并记录日志
    time.sleep(10)

    # 验证健康检查线程仍在运行
    assert process_manager.health_check_thread.is_alive()

    # 捕获并验证控制台输出包含预期的消息


    # 最后停止进程
    process_manager.stop()

    # 验证进程已完全终止
    time.sleep(1)
    assert not process_manager.is_ready()
    assert not process_manager.is_alive()


def test_wait_until_ready_timeout(process_manager):
    script_path = Path(__file__).parent / "mock_never_ready_process.py"

    # 创建一个永不就绪的mock进程脚本
    with open(script_path, 'w') as f:
        f.write('''
            import time
            while True:
                time.sleep(1)
            ''')

    # 启动进程
    command = ['python3', str(script_path)]
    process_manager.start(command)

    # 设置一个较短的超时时间进行测试
    short_timeout = 3

    # 验证等待超时会抛出RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        process_manager.wait_until_ready(timeout=short_timeout)

    assert "Process startup timed out" in str(exc_info.value)

    # 清理临时文件
    script_path.unlink()


@pytest.fixture(autouse=True)
def cleanup(process_manager):
    yield
    if process_manager.process:
        process_manager.stop()
        time.sleep(1)  # 确保进程完全终止
