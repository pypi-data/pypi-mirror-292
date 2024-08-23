import logging
from datetime import datetime
from pathlib import Path

from lightdb import LightDB

_logger = logging.getLogger(__name__)


class SyncMeta:
    def __init__(self, db_path: Path):
        self._db = LightDB(str(db_path.absolute()))

    @property
    def last_sync_time(self) -> datetime:
        if "last" not in self._db:
            return datetime.min
        else:
            return datetime.fromisoformat(self._db["last"])

    def update_last_sync_time(self):
        self._db["last"] = datetime.now().isoformat()
        self._db.save()
