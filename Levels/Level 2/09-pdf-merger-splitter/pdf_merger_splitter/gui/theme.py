from __future__ import annotations

from textwrap import dedent

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


_FONT_STACK = "'Segoe UI', 'Helvetica Neue', 'San Francisco', 'Roboto', Arial, sans-serif"

_LIGHT_COLORS: dict[str, str] = {
    "window": "#f4f6fb",
    "panel": "#eef2f8",
    "card": "#ffffff",
    "base": "#ffffff",
    "border": "#d5dbe8",
    "border_strong": "#bbc5d8",
    "text": "#0f172a",
    "subtext": "#475569",
    "muted": "#94a3b8",
    "accent": "#3867ff",
    "accent_hover": "#2f56d3",
    "accent_active": "#2747ad",
    "accent_soft": "#e1eaff",
    "selection": "#3156e0",
    "selection_text": "#ffffff",
    "toolbar": "#e8edf7",
    "status": "#ffffff",
    "input_bg": "#ffffff",
    "shadow": "rgba(15, 23, 42, 0.08)",
}

_DARK_COLORS: dict[str, str] = {
    "window": "#0b1220",
    "panel": "#121b2d",
    "card": "#17243d",
    "base": "#111a2c",
    "border": "#22314d",
    "border_strong": "#324468",
    "text": "#e2e8f0",
    "subtext": "#c4d0e8",
    "muted": "#8b9bbd",
    "accent": "#5a8bff",
    "accent_hover": "#4877e6",
    "accent_active": "#375cc2",
    "accent_soft": "rgba(90, 139, 255, 0.16)",
    "selection": "#4877e6",
    "selection_text": "#0b1220",
    "toolbar": "#121b30",
    "status": "#121b30",
    "input_bg": "#192943",
    "shadow": "rgba(8, 12, 20, 0.55)",
}


def _build_palette(colors: dict[str, str]) -> QPalette:
    palette = QPalette()

    window = QColor(colors["window"])
    base = QColor(colors["base"])
    card = QColor(colors["card"])
    text = QColor(colors["text"])
    subtext = QColor(colors["subtext"])
    muted = QColor(colors["muted"])
    border = QColor(colors["border"])
    highlight = QColor(colors["selection"])
    highlight_text = QColor(colors["selection_text"])

    for group in (QPalette.Active, QPalette.Inactive):
        palette.setColor(group, QPalette.Window, window)
        palette.setColor(group, QPalette.WindowText, text)
        palette.setColor(group, QPalette.Base, base)
        palette.setColor(group, QPalette.AlternateBase, card)
        palette.setColor(group, QPalette.ToolTipBase, card)
        palette.setColor(group, QPalette.ToolTipText, text)
        palette.setColor(group, QPalette.Text, text)
        palette.setColor(group, QPalette.Button, card)
        palette.setColor(group, QPalette.ButtonText, text)
        palette.setColor(group, QPalette.Link, highlight)
        palette.setColor(group, QPalette.Highlight, highlight)
        palette.setColor(group, QPalette.HighlightedText, highlight_text)
        palette.setColor(group, QPalette.BrightText, QColor("#ff6b6b"))
        palette.setColor(group, QPalette.Mid, border)
        palette.setColor(group, QPalette.Midlight, QColor(colors["border_strong"]))
        palette.setColor(group, QPalette.Light, QColor(colors["border_strong"]))
        palette.setColor(group, QPalette.Dark, border.darker(150))

    palette.setColor(QPalette.Disabled, QPalette.Text, muted)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, muted)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, muted)
    palette.setColor(QPalette.Disabled, QPalette.Highlight, border)
    palette.setColor(QPalette.Disabled, QPalette.HighlightedText, muted)
    palette.setColor(QPalette.PlaceholderText, subtext)

    return palette


def _build_stylesheet(colors: dict[str, str]) -> str:
    return dedent(
        f"""
        QWidget {{
            font-family: {_FONT_STACK};
            font-size: 13px;
            color: {colors["text"]};
            background-color: {colors["window"]};
        }}

        QToolBar {{
            background: {colors["toolbar"]};
            border: none;
            border-bottom: 1px solid {colors["border"]};
            padding: 6px 8px;
            spacing: 8px;
        }}

        QToolButton {{
            border-radius: 6px;
            padding: 6px 12px;
            background: transparent;
            color: {colors["text"]};
        }}

        QToolButton:hover {{
            background: {colors["accent_soft"]};
            color: {colors["accent"]};
        }}

        QToolButton:pressed {{
            background: {colors["accent_hover"]};
            color: {colors["selection_text"]};
        }}

        QStatusBar {{
            background: {colors["status"]};
            border-top: 1px solid {colors["border"]};
        }}

        QStatusBar::item {{
            border: none;
        }}

        QMenu {{
            background-color: {colors["card"]};
            border: 1px solid {colors["border"]};
            padding: 6px;
        }}

        QMenu::item {{
            padding: 6px 14px;
            border-radius: 4px;
            color: {colors["text"]};
        }}

        QMenu::item:selected {{
            background-color: {colors["accent_soft"]};
            color: {colors["accent"]};
        }}

        QTabWidget::pane {{
            border: none;
            background: {colors["card"]};
        }}

        QTabBar::tab {{
            background: transparent;
            border-bottom: 2px solid transparent;
            padding: 10px 18px;
            color: {colors["muted"]};
            font-weight: 500;
        }}

        QTabBar::tab:selected {{
            color: {colors["text"]};
            border-color: {colors["accent"]};
        }}

        QTabBar::tab:hover {{
            color: {colors["accent"]};
        }}

        QTabBar::tab:!selected {{
            margin-top: 2px;
        }}

        QSplitter::handle {{
            background: {colors["border"]};
            width: 4px;
            margin: 0 6px;
            border-radius: 2px;
        }}

        QSplitter::handle:hover {{
            background: {colors["accent"]};
        }}

        QScrollArea {{
            border: none;
            background: transparent;
        }}

        QScrollArea QWidget {{
            background: transparent;
        }}

        QLabel, QCheckBox, QRadioButton {{
            color: {colors["text"]};
        }}

        QLabel[class~="thumbnailCaption"] {{
            color: {colors["subtext"]};
            font-size: 12px;
            font-weight: 600;
        }}

        QLabel[class~="secondaryText"] {{
            color: {colors["muted"]};
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors["border"]};
            border-radius: 4px;
            background: {colors["card"]};
        }}

        QCheckBox::indicator:hover {{
            border-color: {colors["accent"]};
        }}

        QCheckBox::indicator:checked {{
            border-color: {colors["accent"]};
            background-color: {colors["accent"]};
            image: none;
        }}

        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {colors["border"]};
            border-radius: 9px;
            background: {colors["card"]};
            margin-right: 6px;
        }}

        QRadioButton::indicator:hover {{
            border-color: {colors["accent"]};
        }}

        QRadioButton::indicator:checked {{
            border-color: {colors["accent"]};
            background-color: {colors["accent"]};
        }}

        QPushButton {{
            background-color: {colors["accent"]};
            color: {colors["selection_text"]};
            border: none;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {colors["accent_hover"]};
        }}

        QPushButton:pressed {{
            background-color: {colors["accent_active"]};
        }}

        QPushButton:disabled {{
            background-color: {colors["border"]};
            color: {colors["muted"]};
        }}

        QPushButton[class~="secondary"] {{
            background-color: transparent;
            color: {colors["accent"]};
            border: 1px solid {colors["accent"]};
        }}

        QPushButton[class~="secondary"]:hover {{
            background-color: {colors["accent_soft"]};
        }}

        QPushButton[class~="secondary"]:pressed {{
            background-color: {colors["accent_hover"]};
            color: {colors["selection_text"]};
        }}

        QPushButton[class~="secondary"]:disabled {{
            border-color: {colors["border"]};
            color: {colors["muted"]};
            background-color: transparent;
        }}

        QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background: {colors["input_bg"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 6px;
            padding: 6px 10px;
        }}

        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {colors["accent"]};
        }}

        QComboBox::drop-down {{
            width: 28px;
            border: none;
            border-left: 1px solid {colors["border"]};
        }}

        QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
            margin-right: 8px;
        }}

        QProgressBar {{
            background-color: {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 8px;
            text-align: center;
            padding: 2px;
        }}

        QProgressBar::chunk {{
            background-color: {colors["accent"]};
            border-radius: 6px;
        }}

        QScrollBar:vertical {{
            width: 12px;
            background: transparent;
            margin: 4px;
        }}

        QScrollBar::handle:vertical {{
            background: {colors["border_strong"]};
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {colors["accent"]};
        }}

        QScrollBar:horizontal {{
            height: 12px;
            background: transparent;
            margin: 4px;
        }}

        QScrollBar::handle:horizontal {{
            background: {colors["border_strong"]};
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {colors["accent"]};
        }}

        QMessageBox {{
            background-color: {colors["card"]};
        }}

        QWidget#previewPanel {{
            background-color: {colors["card"]};
            border-radius: 16px;
        }}

        QLabel#previewPlaceholder {{
            color: {colors["subtext"]};
            border: 1px dashed {colors["border"]};
            border-radius: 16px;
            padding: 24px 16px;
            background-color: {colors["card"]};
        }}

        QWidget#operationView {{
            background-color: {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 16px;
        }}

        QFrame[variant="thumbnail"] {{
            background-color: {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 12px;
        }}

        QFrame[variant="thumbnail"]:hover {{
            border-color: {colors["accent"]};
        }}

        QFrame[variant="thumbnail"][selected="true"] {{
            border: 2px solid {colors["accent"]};
            background-color: {colors["accent_soft"]};
        }}

        QListWidget {{
            background: {colors["card"]};
            border: 1px solid {colors["border"]};
            border-radius: 12px;
            padding: 6px;
        }}

        QListWidget::item {{
            border-radius: 8px;
            padding: 8px 12px;
            color: {colors["text"]};
        }}

        QListWidget::item:selected {{
            background: {colors["accent_soft"]};
            color: {colors["accent"]};
        }}

        QListWidget::item:hover {{
            background: {colors["accent_soft"]};
        }}

        QGroupBox {{
            border: 1px solid {colors["border"]};
            border-radius: 8px;
            margin-top: 12px;
            padding: 10px 10px 10px 14px;
            background-color: {colors["card"]};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 4px;
            color: {colors["subtext"]};
        }}
        """
    ).strip()


def apply_dark_palette(app: QApplication) -> None:
    palette = _build_palette(_DARK_COLORS)
    app.setPalette(palette)
    app.setStyleSheet(_build_stylesheet(_DARK_COLORS))


def apply_light_palette(app: QApplication) -> None:
    palette = _build_palette(_LIGHT_COLORS)
    app.setPalette(palette)
    app.setStyleSheet(_build_stylesheet(_LIGHT_COLORS))
