import logging
from typing import *

from qcanvas_backend.task_master.task_master import Reporter

_logger = logging.getLogger(__name__)


class AtomicTaskReporter(Reporter):

    def __init__(self, goal_name: str, step_name: str):
        super().__init__(goal_name, step_name)

    def start(self) -> None:
        self.ensure_task_master_assigned()
        self.task_master.report_progress(self.task_id, 0, 0)

    def finish(self) -> None:
        self.ensure_task_master_assigned()
        self.task_master.report_progress(self.task_id, 1, 1)

    def __enter__(self) -> Self:
        self.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            self.failed(exc_val)
        else:
            self.finish()
