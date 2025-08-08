from functools import partial
from typing import Callable

from PySide6.QtCore import QObject, qCritical

from src.databases.local.local_db import SessionLocal
from src.databases.models.models import CabinsDB
from src.databases.schemes.schemas import Cabin
from src.databases.utilities.base_repository import BaseRepository
from src.databases.utilities.workers import DBWorker

_ID_TAG = "[CABIN_REPO]"


def get_all_cabins() -> list[Cabin]:
    with SessionLocal() as db:
        db_items = db.query(CabinsDB).all()
        return [Cabin.model_validate(item) for item in db_items]


def add_cabin(scheme: Cabin) -> None:
    with SessionLocal() as db:
        db.add(CabinsDB(**scheme.model_dump()))

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise e


# noinspection DuplicatedCode
class CabinRepository(BaseRepository):
    @staticmethod
    def get_all_cabins(
            parent: QObject | None = None,
            on_result: Callable[[list[Cabin]], None] = lambda *_: None,
            on_error: Callable[[str], None] = lambda err: qCritical(f"{_ID_TAG} {err}"),
            on_finished: Callable[[], None] = lambda: None,
            *args, **kwargs
    ) -> DBWorker:
        return BaseRepository.run_async(get_all_cabins, Cabin, parent,
                                        on_result, on_error, on_finished,
                                        *args, **kwargs)

    @staticmethod
    def add_cabin(
            scheme: Cabin,
            parent: QObject = None,
            on_result: Callable[[None], None] = lambda *_: None,
            on_error: Callable[[str], None] = lambda err: qCritical(f"{_ID_TAG} {err}"),
            on_finished: Callable[[], None] = lambda: None,
            *args, **kwargs
    ) -> DBWorker:
        fn = partial(add_cabin, scheme)
        return BaseRepository.run_async(fn, Cabin, parent,
                                        on_result, on_error, on_finished,
                                        *args, **kwargs)
