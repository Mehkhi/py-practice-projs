import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from task_scheduler.core import Task, Scheduler
from task_scheduler.utils import CronExpressionError


def test_task_creation():
    task = Task('test', '* * * * *', 'shell', 'echo hello')
    assert task.id == 'test'
    assert task.cron_expr == '* * * * *'
    assert task.task_type == 'shell'
    assert task.command == 'echo hello'
    assert task.retries == 3


def test_get_next_run():
    task = Task('test', '0 * * * *', 'shell', 'echo hello')  # Every hour at minute 0
    next_run = task.get_next_run()
    assert next_run > datetime.now()


def test_get_next_run_advances_between_calls():
    task = Task('test', '*/15 * * * *', 'shell', 'echo hello')
    first = task.get_next_run()
    second = task.get_next_run()
    assert second > first
    assert second - first == timedelta(minutes=15)


@patch('subprocess.run')
def test_execute_shell_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stderr='')
    task = Task('test', '* * * * *', 'shell', 'echo hello')
    task.execute()
    mock_run.assert_called_once_with('echo hello', shell=True, capture_output=True, text=True, timeout=300)


@patch('subprocess.run')
def test_execute_shell_failure_retry(mock_run):
    mock_run.side_effect = [MagicMock(returncode=1, stderr='error'), MagicMock(returncode=0, stderr='')]
    task = Task('test', '* * * * *', 'shell', 'echo hello', retries=1)
    task.execute()
    assert mock_run.call_count == 2


@patch('importlib.import_module')
def test_execute_python_success(mock_import):
    mock_mod = MagicMock()
    mock_func = MagicMock()
    mock_mod.test_func = mock_func
    mock_import.return_value = mock_mod
    task = Task('test', '* * * * *', 'python', '', module='test_mod', function='test_func')
    task.execute()
    mock_import.assert_called_with('test_mod')
    mock_func.assert_called_once()


@patch('importlib.import_module')
def test_execute_python_failure_retry(mock_import):
    mock_mod = MagicMock()
    mock_func = MagicMock(side_effect=Exception('fail'))
    mock_mod.test_func = mock_func
    mock_import.return_value = mock_mod
    task = Task('test', '* * * * *', 'python', '', module='test_mod', function='test_func', retries=1)
    task.execute()
    # First call fails, second succeeds (but since side_effect is always fail, it will fail twice)
    # Actually, for retry, it will call again, but since mock is same, it fails.
    # But assert called twice
    assert mock_func.call_count == 2


def test_scheduler_add_task(tmp_path):
    scheduler = Scheduler(storage_file=str(tmp_path / 'tasks.json'))
    task = Task('test', '* * * * *', 'shell', 'echo hello')
    scheduler.add_task(task)
    assert len(scheduler.tasks) == 1
    assert scheduler.tasks[0].id == 'test'


def test_scheduler_remove_task(tmp_path):
    scheduler = Scheduler(storage_file=str(tmp_path / 'tasks.json'))
    task = Task('test', '* * * * *', 'shell', 'echo hello')
    scheduler.add_task(task)
    assert scheduler.remove_task('test')
    assert len(scheduler.tasks) == 0
    assert not scheduler.remove_task('nonexistent')


def test_scheduler_list_tasks(tmp_path):
    scheduler = Scheduler(storage_file=str(tmp_path / 'tasks.json'))
    task = Task('test', '* * * * *', 'shell', 'echo hello')
    scheduler.add_task(task)
    tasks = scheduler.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == 'test'


def test_scheduler_load_save(tmp_path):
    storage_file = tmp_path / 'tasks.json'
    scheduler1 = Scheduler(storage_file=str(storage_file))
    task = Task('test', '* * * * *', 'shell', 'echo hello')
    scheduler1.add_task(task)
    # Create new scheduler to test loading
    scheduler2 = Scheduler(storage_file=str(storage_file))
    assert len(scheduler2.tasks) == 1
    assert scheduler2.tasks[0].id == 'test'


def test_invalid_cron_expression_raises():
    with pytest.raises(CronExpressionError):
        Task('bad', 'invalid cron', 'shell', 'echo hello')


@patch('task_scheduler.core.subprocess.run')
def test_scheduler_does_not_advance_future_tasks(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=0, stderr='')

    scheduler = Scheduler(storage_file=str(tmp_path / 'tasks.json'))
    due_task = Task('due', '* * * * *', 'shell', 'echo due')
    future_task = Task('future', '*/5 * * * *', 'shell', 'echo future')

    scheduler.add_task(due_task)
    scheduler.add_task(future_task)

    future_next_time = scheduler._next_runs[future_task]
    original_get_next = future_task.get_next_run
    future_task.get_next_run = MagicMock(side_effect=original_get_next)

    scheduler._next_runs[due_task] = datetime.now()

    with patch('task_scheduler.core.time.sleep', side_effect=KeyboardInterrupt):
        scheduler.run()

    assert mock_run.call_count >= 1
    future_task.get_next_run.assert_not_called()
    assert scheduler._next_runs[future_task] == future_next_time
