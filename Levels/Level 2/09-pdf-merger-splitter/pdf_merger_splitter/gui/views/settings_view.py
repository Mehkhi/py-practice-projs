from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class SettingsView(QWidget):
    """Settings panel for appearance and personalization options."""

    theme_requested = Signal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("operationView")
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        appearance_box = QGroupBox("Appearance", self)
        appearance_layout = QVBoxLayout(appearance_box)
        appearance_layout.setSpacing(12)

        intro = QLabel("Choose how the interface looks. Changes apply instantly.")
        intro.setProperty("class", "secondaryText")
        intro.setWordWrap(True)
        appearance_layout.addWidget(intro)

        self._theme_group = QButtonGroup(self)
        options_row = QHBoxLayout()
        options_row.setSpacing(24)

        self.light_radio = QRadioButton("Light")
        self.dark_radio = QRadioButton("Dark")
        self._theme_group.addButton(self.light_radio)
        self._theme_group.addButton(self.dark_radio)

        options_row.addWidget(self.light_radio)
        options_row.addWidget(self.dark_radio)
        options_row.addStretch(1)
        appearance_layout.addLayout(options_row)

        self._theme_group.buttonToggled.connect(self._on_theme_toggled)

        root.addWidget(appearance_box)
        root.addStretch(1)

    def _on_theme_toggled(self, button: QRadioButton, checked: bool) -> None:
        if not checked:
            return
        self.theme_requested.emit(button is self.dark_radio)

    def sync_theme(self, dark_mode: bool) -> None:
        block = self._theme_group.blockSignals(True)
        self.dark_radio.setChecked(dark_mode)
        self.light_radio.setChecked(not dark_mode)
        self._theme_group.blockSignals(block)
