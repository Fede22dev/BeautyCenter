import traceback
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QRunnable, Signal, QObject


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()

    def __init__(self, parent: QObject | None):
        super().__init__(parent)


class DBWorker(QRunnable):
    def __init__(self, fn: Callable[..., Any], parent: QObject | None, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.parent = parent
        self.signals = WorkerSignals(parent)

    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)

            try:
                if isinstance(result, list):
                    serialized_result = [item.model_dump() for item in result] if result else []
                else:
                    serialized_result = result.model_dump() if result is not None else None
            except Exception as e:
                raise ValueError(f"Error deserialization data: {e}")

            self.signals.result.emit(serialized_result)
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)
        finally:
            self.signals.finished.emit()
