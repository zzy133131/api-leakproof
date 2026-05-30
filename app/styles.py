"""Application stylesheet and theme constants."""
from PySide6.QtGui import QColor, QFont

# ── Color Palette ──────────────────────────────────────────────

class Colors:
    # Backgrounds
    BG_PRIMARY = "#1e1e2e"
    BG_SECONDARY = "#2a2a3c"
    BG_TERTIARY = "#33334a"
    BG_HOVER = "#3a3a52"

    # Text
    TEXT_PRIMARY = "#e0e0f0"
    TEXT_SECONDARY = "#9999b0"
    TEXT_ACCENT = "#7c8cf8"

    # Status
    GREEN = "#4caf93"
    YELLOW = "#f0c060"
    RED = "#e0556a"

    # Borders
    BORDER = "#3a3a52"
    BORDER_ACTIVE = "#7c8cf8"

    # Button
    BTN_PRIMARY = "#7c8cf8"
    BTN_PRIMARY_HOVER = "#949cf9"
    BTN_SECONDARY = "#3a3a52"
    BTN_DANGER = "#e0556a"


# ── Global Stylesheet ──────────────────────────────────────────

STYLESHEET = f"""
QMainWindow {{
    background-color: {Colors.BG_PRIMARY};
    color: {Colors.TEXT_PRIMARY};
}}

QWidget {{
    background-color: transparent;
    color: {Colors.TEXT_PRIMARY};
    font-family: ".AppleSystemUIFont", "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}}

QLabel {{
    color: {Colors.TEXT_PRIMARY};
}}

QLineEdit {{
    background-color: {Colors.BG_TERTIARY};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {Colors.TEXT_PRIMARY};
    font-size: 13px;
}}

QLineEdit:focus {{
    border-color: {Colors.BORDER_ACTIVE};
}}

QPushButton {{
    background-color: {Colors.BTN_PRIMARY};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {Colors.BTN_PRIMARY_HOVER};
}}

QPushButton#secondaryBtn {{
    background-color: {Colors.BTN_SECONDARY};
    color: {Colors.TEXT_PRIMARY};
}}

QPushButton#secondaryBtn:hover {{
    background-color: {Colors.BG_HOVER};
}}

QPushButton#dangerBtn {{
    background-color: {Colors.BTN_DANGER};
}}

QTableWidget {{
    background-color: {Colors.BG_SECONDARY};
    border: 1px solid {Colors.BORDER};
    border-radius: 8px;
    gridline-color: {Colors.BORDER};
    color: {Colors.TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 8px;
}}

QTableWidget::item:selected {{
    background-color: {Colors.BG_TERTIARY};
}}

QHeaderView::section {{
    background-color: {Colors.BG_TERTIARY};
    color: {Colors.TEXT_SECONDARY};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {Colors.BORDER};
    font-weight: 600;
    font-size: 12px;
}}

QScrollBar:vertical {{
    background-color: {Colors.BG_PRIMARY};
    width: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: {Colors.BG_TERTIARY};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QComboBox {{
    background-color: {Colors.BG_TERTIARY};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {Colors.TEXT_PRIMARY};
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.BG_SECONDARY};
    border: 1px solid {Colors.BORDER};
    selection-background-color: {Colors.BG_TERTIARY};
    color: {Colors.TEXT_PRIMARY};
}}

QGroupBox {{
    border: 1px solid {Colors.BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
    color: {Colors.TEXT_SECONDARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}
"""
