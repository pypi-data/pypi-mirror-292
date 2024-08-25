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
            # Stupid workaround for datetime.min.timestamp() producing a fucking ValueError due to it being too small or some shit!!
            # WTF python?!
            return datetime(2, 1, 1, 1, 1, 1, 1)
        else:
            return datetime.fromisoformat(self._db["last"])

    def update_last_sync_time(self):
        self._db["last"] = datetime.now().isoformat()
        self._db.save()
