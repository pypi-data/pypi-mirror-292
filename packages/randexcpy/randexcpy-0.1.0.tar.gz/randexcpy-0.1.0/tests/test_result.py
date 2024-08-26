import pytest
from randexpy.result import Result
from randexpy.exceptions import ExecutionError
from datetime import datetime

def test_result_initialization():
    result = Result()
    assert result.value is None
    assert result.error is None
    assert result.start_time is None
    assert result.end_time is None

def test_result_get_without_start():
    result = Result()
    # Do not set start_time to trigger the ExecutionError
    with pytest.raises(ExecutionError, match="Result not available yet"):
        result.get(timeout=1)

def test_result_get_with_error():
    result = Result()
    result.start_time = datetime.now()  # Set start_time to avoid ExecutionError
    result.error = RuntimeError("Test error")
    with pytest.raises(RuntimeError, match="Test error"):
        result.get()

def test_result_get_successful():
    result = Result()
    result.start_time = datetime.now()
    result.value = "Success"
    assert result.get() == "Success"
