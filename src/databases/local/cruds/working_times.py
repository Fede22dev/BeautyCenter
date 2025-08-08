from functools import partial
from typing import Callable

from PySide6.QtCore import QObject, qCritical

from src.databases.local.local_db import SessionLocal
from src.databases.models.models import WorkingTimesDB
from src.databases.schemes.schemas import WorkingTimes
from src.databases.utilities.base_repository import BaseRepository
from src.databases.utilities.workers import DBWorker

_ID_TAG = "[WORKING_TIMES_REPO]"


def get_working_times() -> WorkingTimes:
    with SessionLocal() as db:
        times = db.query(WorkingTimesDB).first()
        if not times:
            times = WorkingTimesDB()
        return WorkingTimes.model_validate(times)


def set_working_times(scheme: WorkingTimes) -> None:
    with SessionLocal() as db:
        times = db.query(WorkingTimesDB).first()
        if times:
            times.min_start_time = scheme.min_start_time
            times.max_finish_time = scheme.max_finish_time
        else:
            db.add(WorkingTimesDB(**scheme.model_dump()))

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise e


# noinspection DuplicatedCode
class WorkingTimesRepository(BaseRepository):
    @staticmethod
    def get_working_times(
            parent: QObject | None = None,
            on_result: Callable[[WorkingTimes], None] = lambda *_: None,
            on_error: Callable[[str], None] = lambda err: qCritical(f"{_ID_TAG} {err}"),
            on_finished: Callable[[], None] = lambda: None,
            *args, **kwargs
    ) -> DBWorker:
        return BaseRepository.run_async(get_working_times, WorkingTimes, parent,
                                        on_result, on_error, on_finished,
                                        *args, **kwargs)

    @staticmethod
    def set_working_times(
            scheme: WorkingTimes,
            parent: QObject = None,
            on_result: Callable[[None], None] = lambda *_: None,
            on_error: Callable[[str], None] = lambda err: qCritical(f"{_ID_TAG} {err}"),
            on_finished: Callable[[], None] = lambda: None,
            *args, **kwargs
    ) -> DBWorker:
        fn = partial(set_working_times, scheme)
        return BaseRepository.run_async(fn, WorkingTimes, parent,
                                        on_result, on_error, on_finished,
                                        *args, **kwargs)
