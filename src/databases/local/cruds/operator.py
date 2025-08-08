from functools import partial
from typing import Callable

from PySide6.QtCore import qCritical, QObject

from src.databases.local.local_db import SessionLocal
from src.databases.models.models import OperatorsDB
from src.databases.schemes.schemas import Operator
from src.databases.utilities.base_repository import BaseRepository
from src.databases.utilities.workers import DBWorker

_ID_TAG = "[OPERATOR_REPO]"


def get_all_operators() -> list[Operator]:
    with SessionLocal() as db:
        db_items = db.query(OperatorsDB).all()
        return [Operator.model_validate(item) for item in db_items]


# def get_operator_by_name(name: str) -> Operator | None:
#     with SessionLocal() as db:
#         db_item = db.query(OperatorsDB).filter(OperatorsDB.name == name).first()
#         return Operator.model_validate(db_item) if db_item else None


# def add_all_operators(schemes: list[Operator]) -> None:
#     with SessionLocal() as db:
#         db_items = [OperatorsDB(**scheme.model_dump()) for scheme in schemes]
#         db.add_all(db_items)
#
#         try:
#             db.commit()
#         except Exception as e:
#             db.rollback()
#             raise e

# If specify id and this id exist update operator, else add a new operator
def add_or_update_operator(scheme: Operator) -> None:
    with SessionLocal() as db:
        db_item = db.query(OperatorsDB).filter_by(id=scheme.id).first()
        if db_item:
            db_item.name = scheme.name
        else:
            db.add(OperatorsDB(**scheme.model_dump()))

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

def add_operator(scheme: Operator) -> None:
    with SessionLocal() as db:
        db.add(OperatorsDB(**scheme.model_dump()))

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise e


# noinspection DuplicatedCode
class OperatorRepository(BaseRepository):
    @staticmethod
    def get_all_operators(
            parent: QObject | None = None,
            on_result: Callable[[list[Operator]], None] = lambda *_: None,
            on_error: Callable[[str], None] = lambda err: qCritical(f"{_ID_TAG} {err}"),
            on_finished: Callable[[], None] = lambda: None,
            *args, **kwargs
    ) -> DBWorker:
        return BaseRepository.run_async(get_all_operators, Operator, parent,
                                        on_result, on_error, on_finished,
                                        *args, **kwargs)

    # @staticmethod
    # def get_operator_by_name(
    #         name: str,
    #         parent: QObject | None = None,
    #         on_result: Callable[[Operator], None] = lambda *_: None,
    #         on_error: Callable[[str], None] = lambda err: qCritical(f"{_ID_TAG} {err}"),
    #         on_finished: Callable[[], None] = lambda: None,
    #         *args, **kwargs
    # ) -> DBWorker:
    #     fn = partial(get_operator_by_name, name)
    #     return BaseRepository.run_async(fn, Operator, parent,
    #                                     on_result, on_error, on_finished,
    #                                     *args, **kwargs)


    @staticmethod
    def add_or_update_operator(
            scheme: Operator,
            parent: QObject = None,
            on_result: Callable[[None], None] = lambda *_: None,
            on_error: Callable[[str], None] = lambda err: qCritical(f"{_ID_TAG} {err}"),
            on_finished: Callable[[], None] = lambda: None,
            *args, **kwargs
    ) -> DBWorker:
        """If specify id and this id exist update operator, else add a new operator"""

        fn = partial(add_or_update_operator, scheme)
        return BaseRepository.run_async(fn, Operator, parent,
                                        on_result, on_error, on_finished,
                                        *args, **kwargs)


    @staticmethod
    def add_operator(
            scheme: Operator,
            parent: QObject = None,
            on_result: Callable[[None], None] = lambda *_: None,
            on_error: Callable[[str], None] = lambda err: qCritical(f"{_ID_TAG} {err}"),
            on_finished: Callable[[], None] = lambda: None,
            *args, **kwargs
    ) -> DBWorker:
        fn = partial(add_operator, scheme)
        return BaseRepository.run_async(fn, Operator, parent,
                                        on_result, on_error, on_finished,
                                        *args, **kwargs)
