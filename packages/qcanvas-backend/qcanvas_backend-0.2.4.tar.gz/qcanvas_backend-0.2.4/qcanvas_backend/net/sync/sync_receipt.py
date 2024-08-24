import logging
from dataclasses import dataclass, field

import qcanvas_backend.database.types as db
from qcanvas_backend.net.sync.canvas_sync_observer import CanvasSyncObserver

_logger = logging.getLogger(__name__)


@dataclass
class CourseUpdates:
    updated_modules: set[str] = field(default_factory=set)
    updated_pages: set[str] = field(default_factory=set)
    updated_assignment_groups: set[str] = field(default_factory=set)
    updated_assignments: set[str] = field(default_factory=set)
    updated_resources: set[str] = field(default_factory=set)
    updated_messages: set[str | int] = field(default_factory=set)

    def new_content_found(self, content: object) -> None:
        if isinstance(content, db.Module):
            self.updated_modules.add(content.id)
        elif isinstance(content, db.ModulePage):
            self.updated_pages.add(content.id)
            self.updated_modules.add(content.module_id)
        elif isinstance(content, db.CourseMessage):
            self.updated_messages.add(content.id)
        elif isinstance(content, db.AssignmentGroup):
            self.updated_assignment_groups.add(content.id)
        elif isinstance(content, db.Assignment):
            self.updated_assignments.add(content.id)
            self.updated_assignment_groups.add(content.group_id)
        elif isinstance(content, db.Resource):
            self.updated_resources.add(content.id)

    def was_updated(self, content: object) -> bool:
        if isinstance(content, db.Module):
            return content.id in self.updated_modules
        elif isinstance(content, db.ModulePage):
            return content.id in self.updated_pages
        elif isinstance(content, db.CourseMessage):
            return content.id in self.updated_messages
        elif isinstance(content, db.AssignmentGroup):
            return content.id in self.updated_assignment_groups
        elif isinstance(content, db.Assignment):
            return content.id in self.updated_assignments
        elif isinstance(content, db.Resource):
            return content.id in self.updated_resources
        else:
            return False


@dataclass
class SyncReceipt(CanvasSyncObserver, CourseUpdates):
    updated_courses: set[str] = field(default_factory=set)
    updates_by_course: dict[str, CourseUpdates] = field(default_factory=dict)

    def new_content_found(self, content: object) -> None:
        # Need to specify CourseUpdates because of the diamond problem
        CourseUpdates.new_content_found(self, content)

        if isinstance(content, db.Course):
            self.updated_courses.add(content.id)
        else:
            if hasattr(content, "course_id"):
                if content.course_id not in self.updates_by_course:
                    self.updates_by_course[content.course_id] = CourseUpdates()
                    self.updated_courses.add(content.course_id)

                self.updates_by_course[content.course_id].new_content_found(content)

    def was_updated(self, content: object) -> bool:
        if isinstance(content, db.Course):
            return content.id in self.updated_courses
        else:
            return super().was_updated(content)


_empty = SyncReceipt()


def empty_receipt() -> SyncReceipt:
    global _empty
    return _empty
