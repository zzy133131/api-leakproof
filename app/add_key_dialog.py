"""Dialog for adding a new API key to monitor."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox,
)
from PySide6.QtCore import Qt
from cryptography.fernet import Fernet

from config.settings import DATA_DIR
from db.database import insert_key
from shared.types import MonitoredKey, Platform

# Generate or load encryption key
KEY_FILE = DATA_DIR / ".encryption_key"


def _get_cipher() -> Fernet:
    if KEY_FILE.exists():
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    return Fernet(key)


def encrypt_api_key(plain_key: str) -> str:
    cipher = _get_cipher()
    return cipher.encrypt(plain_key.encode()).decode()


def decrypt_api_key(encrypted: str) -> str:
    cipher = _get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()


class AddKeyDialog(QDialog):
    """Dialog to add a new API key for monitoring."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加监控 Key")
        self.setFixedSize(440, 320)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("添加 API Key")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        # Platform selector
        layout.addWidget(QLabel("平台"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["OpenAI", "Claude", "DeepSeek", "Qwen", "自定义"])
        layout.addWidget(self.platform_combo)

        # API Key input
        layout.addWidget(QLabel("API Key"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("sk-... 或 ds-...")
        self.key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.key_input)

        # Custom base URL (shown only for custom)
        layout.addWidget(QLabel("自定义 Base URL（可选）"))
        self.custom_url = QLineEdit()
        self.custom_url.setPlaceholderText("https://api.example.com")
        layout.addWidget(self.custom_url)

        layout.addStretch()

        # Buttons
        btns = QHBoxLayout()
        cancel = QPushButton("取消")
        cancel.setObjectName("secondaryBtn")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)

        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self._add_key)
        btns.addWidget(add_btn)
        layout.addLayout(btns)

    def _add_key(self):
        plain_key = self.key_input.text().strip()
        if not plain_key:
            QMessageBox.warning(self, "输入错误", "请输入 API Key")
            return

        platform_map = {
            0: Platform.OPENAI,
            1: Platform.CLAUDE,
            2: Platform.DEEPSEEK,
            3: Platform.QWEN,
            4: Platform.CUSTOM,
        }
        platform = platform_map[self.platform_combo.currentIndex()]

        encrypted = encrypt_api_key(plain_key)
        key = MonitoredKey(
            key_prefix=plain_key[:8],
            key_encrypted=encrypted,
            platform=platform,
            custom_base_url=self.custom_url.text().strip() or None,
            alert_enabled=True,
        )
        insert_key(key)
        self.accept()
