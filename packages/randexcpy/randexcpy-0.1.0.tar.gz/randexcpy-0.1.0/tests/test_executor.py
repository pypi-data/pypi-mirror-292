import time
import pytest
from datetime import timedelta
from randexpy.executor import Executor, ExecutionError

def test_execute():
    executor = Executor(max_duration="2s", seed=42)
    result = executor.execute(lambda: "test")
    assert result == "test"

def test_execute_timeout():
    executor = Executor(max_duration="3s", seed=42)
    with pytest.raises(ExecutionError, match="Execution timeout exceeded"):
        executor.execute(lambda: time.sleep(5), timeout=1)


def test_execute_exception_handling():
    executor = Executor(max_duration="2s", seed=42)
    with pytest.raises(ExecutionError, match="Execution failed"):
        executor.execute(lambda: 1 / 0)  # Division by zero should raise an exception

def test_execute_async():
    executor = Executor(max_duration="2s", seed=42)
    async_result = executor.execute_async(lambda: "async_test")
    time.sleep(0.1)  # Add a short delay to allow async execution to start
    assert async_result.get(timeout=5) == "async_test"

def test_execute_async_result_error():
    executor = Executor(max_duration="1s", seed=42)
    async_result = executor.execute_async(lambda: 1 / 0)  # This should raise a ZeroDivisionError
    with pytest.raises(ZeroDivisionError):
        async_result.get(timeout=2)
    assert async_result.error is not None
    assert async_result.end_time is not None

def test_parse_duration():
    assert Executor._parse_duration("10s") == timedelta(seconds=10)
    assert Executor._parse_duration("5m") == timedelta(minutes=5)
    assert Executor._parse_duration("1h") == timedelta(hours=1)
    with pytest.raises(ValueError, match="Invalid duration unit"):
        Executor._parse_duration("10x")
