import time

import pytest
from unittest.mock import Mock, patch
from services.management_service import ManagementService, BackendStatus
from concurrent.futures import ThreadPoolExecutor, as_completed


@pytest.fixture
def mock_process_mgr():
    with patch('services.process.process_manager.ProcessManager') as mock:
        instance = mock.return_value
        instance.start = Mock()
        instance.wait_until_ready = Mock(side_effect=lambda: time.sleep(1))
        instance.stop = Mock()
        yield instance


@pytest.fixture
def mock_snapshot_mgr():
    with patch('services.workspace.snapshot_manager.SnapshotManager') as mock:
        instance = mock.return_value
        instance.load = Mock(side_effect=lambda: time.sleep(1))
        instance.save = Mock(side_effect=lambda: time.sleep(1))
        yield instance


@pytest.fixture
def service(mock_process_mgr, mock_snapshot_mgr):
    service = ManagementService()
    service._process_mgr = mock_process_mgr
    service._snapshot_mgr = mock_snapshot_mgr
    return service


def test_concurrent_start(service, mock_process_mgr, mock_snapshot_mgr):
    thread_count = 3

    def start_service():
        try:
            initial_status = service.status
            service.start()
            return {
                'success': True,
                'initial_status': initial_status,
                'final_status': service.status
            }
        except RuntimeError as e:
            return {
                'success': False,
                'initial_status': initial_status,
                'final_status': service.status,
                'error': str(e)
            }

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(start_service) for _ in range(thread_count)]
        start_attempts = [f.result() for f in as_completed(futures)]

    # 验证结果
    successful_starts = [attempt for attempt in start_attempts if attempt['success']]
    failed_starts = [attempt for attempt in start_attempts if not attempt['success']]

    # 应该只有一个成功的启动
    assert len(successful_starts) == 1
    assert len(failed_starts) == thread_count - 1

    # 验证成功的启动状态转换正确
    successful_start = successful_starts[0]
    assert successful_start['initial_status'] == BackendStatus.STOPPED
    assert successful_start['final_status'] == BackendStatus.RUNNING

    # 验证失败的启动包含适当的错误信息
    for failed_start in failed_starts:
        assert "Illegal state transition" in failed_start['error']

    # 验证最终状态和调用次数
    assert service.status == BackendStatus.RUNNING
    assert mock_snapshot_mgr.load.call_count == 1
    assert mock_process_mgr.start.call_count == 1
    assert mock_process_mgr.wait_until_ready.call_count == 1


def test_start_during_starting_fails(service):
    """测试在启动过程中再次调用start会失败"""

    def slow_start():
        service._transition_to(BackendStatus.STARTING)
        time.sleep(0.5)  # 模拟启动过程
        service._transition_to(BackendStatus.RUNNING)

    with ThreadPoolExecutor(max_workers=2) as executor:
        # 开始第一次启动
        first_start = executor.submit(slow_start)
        # 稍等一下确保第一次启动已经开始
        time.sleep(0.1)

        # 尝试第二次启动
        with pytest.raises(RuntimeError) as exc_info:
            service.start()

        assert "Illegal state transition" in str(exc_info.value)

        # 等待第一次启动完成
        first_start.result()

    assert service.status == BackendStatus.RUNNING


def test_initial_status(service):
    assert service.status == BackendStatus.STOPPED


def test_start_success(service, mock_process_mgr, mock_snapshot_mgr):
    service.start()

    mock_snapshot_mgr.load.assert_called_once()
    mock_process_mgr.start.assert_called_once()
    mock_process_mgr.wait_until_ready.assert_called_once()
    assert service.status == BackendStatus.RUNNING


def test_start_failure(service, mock_process_mgr, mock_snapshot_mgr):
    mock_process_mgr.start.side_effect = Exception("Start failed")

    with pytest.raises(Exception):
        service.start()

    assert service.status == BackendStatus.STOPPED


def test_save_success(service, mock_snapshot_mgr):
    service._status = BackendStatus.RUNNING
    service.save()

    mock_snapshot_mgr.save.assert_called_once()
    assert service.status == BackendStatus.RUNNING


def test_save_failure(service, mock_snapshot_mgr):
    service._status = BackendStatus.RUNNING
    mock_snapshot_mgr.save.side_effect = Exception("Save failed")

    with pytest.raises(Exception):
        service.save()

    assert service.status == BackendStatus.RUNNING


def test_stop_success(service, mock_process_mgr):
    service._status = BackendStatus.RUNNING
    service.stop()

    mock_process_mgr.stop.assert_called_once()
    assert service.status == BackendStatus.STOPPED


def test_stop_failure(service, mock_process_mgr):
    service._status = BackendStatus.RUNNING
    mock_process_mgr.stop.side_effect = Exception("Stop failed")

    with pytest.raises(Exception):
        service.stop()

    assert service.status == BackendStatus.RUNNING


def test_save_and_stop(service):
    service._status = BackendStatus.RUNNING
    with patch.object(service, 'save') as mock_save:
        with patch.object(service, 'stop') as mock_stop:
            service.save_and_stop()

            mock_save.assert_called_once()
            mock_stop.assert_called_once()


def test_invalid_transition(service):
    with pytest.raises(RuntimeError):
        service._transition_to(BackendStatus.RUNNING)


@pytest.mark.parametrize("current_status,new_status", [
    (BackendStatus.STOPPED, BackendStatus.STARTING),
    (BackendStatus.STARTING, BackendStatus.RUNNING),
    (BackendStatus.RUNNING, BackendStatus.SAVING),
    (BackendStatus.SAVING, BackendStatus.RUNNING),
    (BackendStatus.RUNNING, BackendStatus.STOPPING),
    (BackendStatus.STOPPING, BackendStatus.STOPPED),
])
def test_valid_transitions(service, current_status, new_status):
    service._status = current_status
    service._transition_to(new_status)
    assert service.status == new_status


@pytest.mark.parametrize("current_status,new_status", [
    (BackendStatus.STOPPED, BackendStatus.RUNNING),
    (BackendStatus.RUNNING, BackendStatus.STARTING),
    (BackendStatus.SAVING, BackendStatus.STOPPED),
    (BackendStatus.STOPPING, BackendStatus.SAVING),
])
def test_invalid_transitions(service, current_status, new_status):
    service._status = current_status
    with pytest.raises(RuntimeError):
        service._transition_to(new_status)
