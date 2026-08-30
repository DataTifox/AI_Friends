"""Application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow

from app.main_window_controller import MainWindowController
from core.conversation import ConversationManager
from core.memory import MemoryManager
from core.personality import PersonalityManager
from services.llm.openai_compatible import OpenAICompatibleProvider
from storage.database import Database
from storage.repository import ConversationRepository, MemoryRepository
from storage.settings_repository import SettingsRepository
from ui.generated.main_window import Ui_MainWindow


PROJECT_DIR = Path(__file__).resolve().parent


def main() -> int:
    application = QApplication(sys.argv)
    database = Database(PROJECT_DIR / "data" / "companion.db")
    database.initialize()
    settings_repository = SettingsRepository(PROJECT_DIR / ".env")
    conversation_manager = ConversationManager(
        repository=ConversationRepository(database),
        settings_repository=settings_repository,
        personality_manager=PersonalityManager(PROJECT_DIR / "config" / "personality.json"),
        memory_manager=MemoryManager(MemoryRepository(database)),
        provider_factory=OpenAICompatibleProvider,
    )
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)

    controller = MainWindowController(
        window=window,
        ui=ui,
        settings_repository=settings_repository,
        conversation_manager=conversation_manager,
    )
    window.controller = controller
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
