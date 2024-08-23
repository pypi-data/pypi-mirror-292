import logging
from asyncio import Task
from threading import Lock
from typing import Self

from qcanvas_backend.task_master.task_master import Reporter

_logger = logging.getLogger(__name__)


class CompoundTaskReporter(Reporter):
    def __init__(self, goal_name: str, step_name: str, total_tasks: int):
        super().__init__(goal_name, step_name)
        self._lock = Lock()
        self._total_tasks = total_tasks
        self._complete_tasks = 0

    def __enter__(self) -> Self:
        self.ensure_task_master_assigned()
        self.progress(0, self._total_tasks)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is not None:
            self.failed(exc_val)

    def attach(self, task: Task) -> Task:
        task.add_done_callback(self._increment_progress)
        return task

    def _increment_progress(self, _) -> None:
        # Contention for this should be extremely low, so it shouldn't have much impact on the event loop
        with self._lock:
            self._complete_tasks += 1
            progress = self._complete_tasks

        self.progress(progress, self._total_tasks)
