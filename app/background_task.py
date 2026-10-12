"""Run requests outside the UI thread; widgets are updated through signals."""

import sqlite3
from PySide6.QtCore import QObject, QRunnable, Signal
from services.llm.base import LLMError


class TaskSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class BackgroundTask(QRunnable):
    def __init__(self, action) -> None:
        super().__init__()
        self.action = action
        self.signals = TaskSignals()

    def run(self) -> None:
        try:
            self.signals.result.emit(self.action())
        except (LLMError, ValueError) as error:
            self.signals.error.emit(str(error))
        except (OSError, sqlite3.Error):
            self.signals.error.emit("读取或保存本地数据失败，请检查文件权限和磁盘空间。")
        except Exception as error:
            self.signals.error.emit(f"处理请求失败（{type(error).__name__}），可以稍后重试。")
        finally:
            self.signals.finished.emit()
