from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QPainter, QPalette
from PySide6.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem, QMenu


class FileListWidget(QListWidget):
    """Drag-and-drop file list supporting reorder/remove/clear.

    This is a minimal shell; full context menus and keyboard actions
    will be added in the next task.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self._placeholder_text: str = ""

    # ---- Public API ----
    def add_files(self, paths: Iterable[Path]) -> None:
        for path in paths:
            if path.suffix.lower() == ".pdf" and path.exists():
                item = QListWidgetItem(str(path))
                item.setData(Qt.UserRole, path)
                self.addItem(item)

    def add_folder(self, folder: Path) -> None:
        pdfs = sorted(p for p in folder.glob("*.pdf"))
        self.add_files(pdfs)

    def file_paths(self) -> list[Path]:
        paths: list[Path] = []
        for i in range(self.count()):
            item = self.item(i)
            data = item.data(Qt.UserRole)
            if isinstance(data, Path):
                paths.append(data)
            else:
                paths.append(Path(item.text()))
        return paths

    # ---- Drag and drop ----
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        mime: QMimeData = event.mimeData()
        if mime.hasUrls():
            paths: list[Path] = []
            for url in mime.urls():
                local = Path(url.toLocalFile())
                if local.is_dir():
                    paths.extend(sorted(p for p in local.glob("*.pdf")))
                else:
                    paths.append(local)
            self.add_files(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    # ---- Removal helpers ----
    def remove_selected(self) -> None:
        for item in sorted(self.selectedItems(), key=lambda it: self.row(it), reverse=True):
            row = self.row(item)
            self.takeItem(row)

    # ---- Context menu ----
    def contextMenuEvent(self, event) -> None:  # noqa: D401
        menu = QMenu(self)
        menu.addAction("Remove Selected", self.remove_selected)
        menu.addAction("Clear All", self.clear)
        menu.exec(event.globalPos())

    # ---- Keyboard delete ----
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.remove_selected()
        else:
            super().keyPressEvent(event)

    # ---- Placeholder support ----
    def set_placeholder_text(self, text: str) -> None:
        self._placeholder_text = text
        self.viewport().update()

    def placeholder_text(self) -> str:
        return self._placeholder_text

    def paintEvent(self, event) -> None:  # noqa: D401
        super().paintEvent(event)
        if self.count() == 0 and self._placeholder_text:
            painter = QPainter(self.viewport())
            painter.setPen(self.palette().color(QPalette.Disabled, QPalette.Text))
            rect = self.viewport().rect().adjusted(8, 8, -8, -8)
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, self._placeholder_text)
            painter.end()
