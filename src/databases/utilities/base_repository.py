from typing import Callable, Type, TypeVar, Union

from PySide6.QtCore import QThreadPool, QObject
from pydantic import BaseModel

from src.databases.utilities.workers import DBWorker

T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    @staticmethod
    def run_async(
            crud_fn: Callable,
            model: Type[T],
            parent: QObject | None,
            on_result: Callable[[Union[T, list[T]]], None],
            on_error: Callable[[str], None],
            on_finished: Callable[[], None],
            *args, **kwargs
    ) -> DBWorker:
        def handle_result(result) -> None:
            try:
                if isinstance(result, list):
                    parsed = [model.model_validate(item) for item in result] if result else []
                else:
                    parsed = model.model_validate(result) if result is not None else None

                on_result(parsed)
            except Exception as e:
                on_error(f"Error serialization data: {e}")

        worker = DBWorker(crud_fn, parent, *args, **kwargs)
        if on_result:
            worker.signals.result.connect(handle_result)
        worker.signals.error.connect(on_error)
        worker.signals.finished.connect(on_finished)
        QThreadPool.globalInstance().start(worker)
        return worker
