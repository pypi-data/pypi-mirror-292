import random
import time
import threading
from datetime import datetime, timedelta
from typing import Callable, Optional, Any, Union

from .result import Result
from .exceptions import ExecutionError  # Updated import

class Executor:
    """
    The Executor class manages the random execution of actions within a specified time frame.
    """

    def __init__(self, max_duration: Union[str, timedelta], seed: Optional[int] = None) -> None:
        if isinstance(max_duration, str):
            max_duration = self._parse_duration(max_duration)
        if not isinstance(max_duration, timedelta):
            raise ValueError("max_duration must be a valid duration string or timedelta")
        self.max_duration = max_duration
        self.rand = random.Random(seed)

    def execute(self, action: Callable[[], Any], timeout: Optional[float] = None) -> Any:
        delay = self._get_random_delay()
        start_time = time.time()
        if timeout and delay > timeout:
            raise ExecutionError("Execution timeout exceeded")
        time.sleep(delay)
        try:
            result = action()
        except Exception as e:
            raise ExecutionError(f"Execution failed: {str(e)}") from e
        if timeout and (time.time() - start_time) > timeout:
            raise ExecutionError("Execution timeout exceeded")
        return result

    def execute_async(self, action: Callable[[], Any]) -> Result:
        result = Result()
        threading.Thread(target=self._async_execution, args=(action, result)).start()
        return result

    def _async_execution(self, action: Callable[[], Any], result: Result) -> None:
        delay = self._get_random_delay()
        time.sleep(delay)
        result.start_time = datetime.now()
        try:
            result.value = action()
            result.error = None
        except Exception as e:
            result.error = e
        result.end_time = datetime.now()

    def _get_random_delay(self) -> float:
        return self.rand.uniform(0, self.max_duration.total_seconds())

    @staticmethod
    def _parse_duration(duration_str: str) -> timedelta:
        unit = duration_str[-1]
        value = int(duration_str[:-1])
        if unit == 's':
            return timedelta(seconds=value)
        elif unit == 'm':
            return timedelta(minutes=value)
        elif unit == 'h':
            return timedelta(hours=value)
        else:
            raise ValueError(f"Invalid duration unit: {unit}")
