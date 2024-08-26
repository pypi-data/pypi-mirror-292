import time
from datetime import datetime
from typing import Optional, Any
from .exceptions import ExecutionError  # Updated import

class Result:
    """
    The Result class represents the outcome of an execution.
    """

    def __init__(self) -> None:
        self.value: Optional[Any] = None
        self.error: Optional[Exception] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def get(self, timeout: Optional[float] = None) -> Any:
        if timeout:
            end_time = time.time() + timeout
            while self.start_time is None and time.time() < end_time:
                time.sleep(0.01)
        if self.start_time is None:
            raise ExecutionError("Result not available yet")
        if self.error:
            raise self.error
        return self.value
