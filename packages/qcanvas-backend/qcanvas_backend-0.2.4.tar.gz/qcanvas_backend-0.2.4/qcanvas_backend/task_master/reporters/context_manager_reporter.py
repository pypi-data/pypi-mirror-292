import logging
from typing import *

from qcanvas_backend.task_master.task_master import Reporter

_logger = logging.getLogger(__name__)


class ContextManagerReporter(Reporter):
    def __init__(self, goal_name: str, step_name: str, total_work: int):
        super().__init__(goal_name, step_name)
        self._total = total_work

    def __enter__(self) -> Self:
        self.ensure_task_master_assigned()
        self.progress(0, self._total)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            self.failed(exc_val)
