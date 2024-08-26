import logging
from asyncio import BoundedSemaphore
from pathlib import Path
from typing import Generic, Optional, Type, TypeVar

from qcanvas_api_clients.canvas import CanvasClient, CanvasClientConfig
from qcanvas_api_clients.panopto import (
    FakePanoptoClient,
    PanoptoClient,
    PanoptoClientConfig,
)

import qcanvas_backend.database.types as db
from qcanvas_backend.database import QCanvasDatabase
from qcanvas_backend.database.data_monolith import DataMonolith
from qcanvas_backend.net.resources.download.resource_manager import ResourceManager
from qcanvas_backend.net.resources.extracting import (
    CanvasFileExtractor,
    CanvasMediaObjectExtractor,
    EmbeddedPanoptoExtractor,
)
from qcanvas_backend.net.resources.extracting.extractors import Extractors
from qcanvas_backend.net.resources.extracting.link_extractor import LinkExtractor
from qcanvas_backend.net.sync.sync_receipt import SyncReceipt
from qcanvas_backend.net.sync.synchronization_client import SynchronizationClient
from qcanvas_backend.task_master import register_reporter
from qcanvas_backend.task_master.reporters import AtomicTaskReporter

U = TypeVar("U", bound=ResourceManager)

_logger = logging.getLogger(__name__)


class QCanvas(Generic[U]):
    def __init__(
        self,
        canvas_config: CanvasClientConfig,
        panopto_config: Optional[PanoptoClientConfig],
        storage_path: Path,
        resource_manager_class: Type[U],
    ):
        storage_path.mkdir(parents=True, exist_ok=True)

        self._data_cache = None
        self._cache_semaphore = BoundedSemaphore()
        self.canvas_client = CanvasClient(client_config=canvas_config)

        if panopto_config is None:
            self.panopto_client = FakePanoptoClient()
        else:
            self.panopto_client = PanoptoClient(
                client_config=panopto_config, canvas_client=self.canvas_client
            )

        self.database = QCanvasDatabase(storage_path / "qcanvas.db")
        self.resource_manager: U = self._create_resource_manager(
            manager=resource_manager_class,
            database=self.database,
            download_dest=storage_path / "downloads",
            extractors=Extractors(*self._create_extractors()),
        )
        self._synchronization_client = SynchronizationClient(
            database=self.database,
            canvas_client=self.canvas_client,
            panopto_client=self.panopto_client,
            resource_scanner=self.resource_manager.scanner,
            sync_meta_store_location=storage_path / "sync_meta.json",
        )
        self._init_called = False

    def _create_extractors(self) -> list[LinkExtractor]:
        result = [
            CanvasFileExtractor(self.canvas_client),
            CanvasMediaObjectExtractor(self.canvas_client),
        ]

        if not isinstance(self.panopto_client, FakePanoptoClient):
            result.append(
                EmbeddedPanoptoExtractor(self.canvas_client, self.panopto_client)
            )

        return result

    @staticmethod
    def _create_resource_manager(
        manager: Type[U],
        database: QCanvasDatabase,
        download_dest: Path,
        extractors: Extractors,
    ) -> ResourceManager:
        return manager(
            database=database, download_dest=download_dest, extractors=extractors
        )

    async def init(self) -> None:
        await self.database.init()
        self.resource_manager.add_existing_resources(
            await self.database.get_existing_resources()
        )

        self._init_called = True

    async def synchronise_canvas(self, quick_sync: bool = False) -> SyncReceipt:
        assert self._init_called
        _logger.info("Synchronising")

        receipt = await self._synchronization_client.synchronise_canvas(
            include_old_courses=quick_sync
        )
        await self._reload_data()
        return receipt

    async def _reload_data(self) -> None:
        self._data_cache = None
        await self.get_data()

    async def download(self, resource: db.Resource) -> None:
        assert self._init_called
        _logger.info(
            "Downloading %s (course_id=%s)", resource.file_name, resource.course_id
        )

        await self.resource_manager.download(resource)

    async def get_data(self) -> DataMonolith:
        assert self._init_called

        async with self._cache_semaphore:
            if self._data_cache is None:
                _logger.info("Loading all data from database")

                # Reading the entire DB can take a few seconds (especially when in portable mode on a shitty usb stick)
                with register_reporter(AtomicTaskReporter("Load", "Read database")):
                    self._data_cache = await self.database.get_data()

            return self._data_cache
