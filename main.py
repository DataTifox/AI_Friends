"""Application entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from app.main_window_controller import MainWindowController
from core.conversation import ConversationManager
from core.followup import FollowupManager
from core.memory import MemoryManager
from core.personality import PersonalityManager
from core.summary import SummaryManager
from services.llm.openai_compatible import OpenAICompatibleProvider
from storage.database import Database
from storage.repository import ConversationRepository, MemoryRepository
from storage.followup_repository import FollowupRepository
from storage.summary_repository import SummaryRepository
from storage.settings_repository import SettingsRepository
from storage.companion_policy_repository import CompanionPolicyRepository
from ui.generated.main_window import Ui_MainWindow


PROJECT_DIR = Path(__file__).resolve().parent


def main() -> int:
    application = QApplication(sys.argv)
    database = Database(PROJECT_DIR / "data" / "companion.db")
    database.initialize()
    settings_repository = SettingsRepository(PROJECT_DIR / ".env")
    policy_repository = CompanionPolicyRepository(PROJECT_DIR / "config" / "companion.json")
    policy = policy_repository.load()
    repository = ConversationRepository(database)
    conversation_manager = ConversationManager(
        repository=repository,
        settings_repository=settings_repository,
        personality_manager=PersonalityManager(PROJECT_DIR / "config" / "personality.json"),
        memory_manager=MemoryManager(MemoryRepository(database)),
        provider_factory=OpenAICompatibleProvider,
        summary_manager=SummaryManager(repository, SummaryRepository(database), policy),
        followup_manager=FollowupManager(FollowupRepository(database), policy),
        policy=policy,
    )
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)

    controller = MainWindowController(
        window=window,
        ui=ui,
        settings_repository=settings_repository,
        conversation_manager=conversation_manager,
        policy_repository=policy_repository,
    )
    window.controller = controller
    window.show()
    return application.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        application = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "启动失败", f"无法启动程序：{error}")
        raise SystemExit(1)
