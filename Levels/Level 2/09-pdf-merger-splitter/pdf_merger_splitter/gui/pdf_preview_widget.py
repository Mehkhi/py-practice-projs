from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QImage, QPixmap
from PySide6.QtPdf import QPdfDocument
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QMessageBox,
    QScrollArea,
    QStackedLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


@dataclass
class _DocumentRecord:
    path: Path
    document: QPdfDocument
    thumbnails: list[QPixmap]


class PageThumbnail(QFrame):
    """Clickable PDF page thumbnail."""

    clicked = Signal(int)

    def __init__(self, page_index: int, pixmap: QPixmap, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.page_index = page_index
        self._selected = False

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setProperty("variant", "thumbnail")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(False)
        layout.addWidget(self.image_label)

        caption = QLabel(f"Page {page_index + 1}")
        caption.setAlignment(Qt.AlignCenter)
        caption.setProperty("class", "thumbnailCaption")
        layout.addWidget(caption)

        self._update_style()

    def mousePressEvent(self, event) -> None:  # noqa: D401
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.page_index)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool) -> None:
        if self._selected == selected:
            return
        self._selected = selected
        self._update_style()

    def _update_style(self) -> None:
        self.setProperty("selected", self._selected)
        # Refresh style so the dynamic property takes effect.
        style = self.style()
        style.unpolish(self)
        style.polish(self)
        self.update()


class PDFPreviewWidget(QWidget):
    """Scrollable preview panel that renders PDF pages as thumbnails."""

    files_dropped = Signal(list)
    document_changed = Signal(object)
    page_clicked = Signal(Path, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("previewPanel")
        self._records: dict[Path, _DocumentRecord] = {}
        self._order: list[Path] = []
        self._current: Path | None = None
        self._current_page: int | None = None
        self._thumbnail_width = 220

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        self.combo = QComboBox(self)
        self.combo.currentIndexChanged.connect(self._on_combo_changed)
        self.combo.setPlaceholderText("No PDF loaded")
        self.combo.setMinimumHeight(36)
        outer.addWidget(self.combo)

        self.placeholder = QLabel("Drop PDF files here or use Add Files to get started.")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setWordWrap(True)
        self.placeholder.setMargin(12)
        self.placeholder.setObjectName("previewPlaceholder")

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        outer.addWidget(self.scroll_area, stretch=1)

        self._stack_widget = QWidget()
        self._stack_layout = QStackedLayout(self._stack_widget)
        self._stack_layout.setContentsMargins(0, 0, 0, 0)

        self._placeholder_container = QWidget()
        placeholder_layout = QVBoxLayout(self._placeholder_container)
        placeholder_layout.setContentsMargins(12, 12, 12, 12)
        placeholder_layout.addStretch(1)
        placeholder_layout.addWidget(self.placeholder, alignment=Qt.AlignCenter)
        placeholder_layout.addStretch(1)
        self._stack_layout.addWidget(self._placeholder_container)

        self._thumb_widget = QWidget()
        self._thumb_layout = QVBoxLayout(self._thumb_widget)
        self._thumb_layout.setAlignment(Qt.AlignTop)
        self._thumb_layout.setContentsMargins(12, 12, 12, 12)
        self._thumb_layout.setSpacing(12)
        self._stack_layout.addWidget(self._thumb_widget)

        self.scroll_area.setWidget(self._stack_widget)
        self._update_placeholder()

    # ---- Public API ----
    def document_paths(self) -> list[Path]:
        return list(self._order)

    def current_document(self) -> Path | None:
        return self._current

    def clear(self) -> None:
        self._records.clear()
        self._order.clear()
        self.combo.clear()
        self._current = None
        self._current_page = None
        self._clear_thumbnails()
        self._update_placeholder()

    def add_documents(self, paths: Iterable[Path]) -> list[Path]:
        added: list[Path] = []
        for path in paths:
            if path in self._records:
                continue
            if not path.exists() or path.suffix.lower() != ".pdf":
                continue
            record = self._load_document(path)
            if record is None:
                continue
            self._records[path] = record
            self._order.append(path)
            self.combo.addItem(path.name, path)
            added.append(path)
        if added:
            self.set_current_document(added[-1])
        self._update_placeholder()
        return added

    def set_current_document(self, path: Path | None) -> None:
        if path is None:
            self._activate_document(None)
            return
        if path not in self._records:
            return
        index = self.combo.findData(path)
        if index < 0:
            return
        if self.combo.currentIndex() == index:
            self._activate_document(path)
            return
        block = self.combo.blockSignals(True)
        self.combo.setCurrentIndex(index)
        self.combo.blockSignals(block)
        self._activate_document(path)

    # ---- Drag and drop ----
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: D401
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: D401
        urls = event.mimeData().urls()
        paths: list[Path] = []
        for url in urls:
            local = Path(url.toLocalFile())
            if local.is_dir():
                paths.extend(p for p in local.glob("*.pdf"))
            else:
                paths.append(local)
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    # ---- Internal helpers ----
    def _update_placeholder(self) -> None:
        record = self._records.get(self._current) if self._current else None
        show_placeholder = not self._order or record is None or not record.thumbnails
        target = self._placeholder_container if show_placeholder else self._thumb_widget
        self._stack_layout.setCurrentWidget(target)

    def _clear_thumbnails(self) -> None:
        while self._thumb_layout.count():
            item = self._thumb_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _load_document(self, path: Path) -> _DocumentRecord | None:
        document = QPdfDocument(self)
        error = document.load(str(path))
        if error != QPdfDocument.Error.None_:
            QMessageBox.warning(
                self,
                "Failed to load PDF",
                f"Could not load {path.name}: {error.name}",
            )
            document.deleteLater()
            return None
        thumbnails = self._render_thumbnails(document)
        return _DocumentRecord(path=path, document=document, thumbnails=thumbnails)

    def _render_thumbnails(self, document: QPdfDocument) -> list[QPixmap]:
        thumbs: list[QPixmap] = []
        count = document.pageCount()
        for page in range(count):
            page_size = document.pagePointSize(page)
            width = page_size.width() or 1.0
            height = page_size.height() or 1.0
            scale = self._thumbnail_width / width
            target = QSize(int(width * scale), int(height * scale))
            image: QImage = document.render(page, target)
            thumbs.append(QPixmap.fromImage(image))
        return thumbs

    def _on_combo_changed(self, index: int) -> None:
        if index < 0 or index >= self.combo.count():
            self._activate_document(None)
            return
        path = Path(self.combo.itemData(index))
        self._activate_document(path)

    def _activate_document(self, path: Path | None) -> None:
        if path is None:
            self._current = None
            self._current_page = None
            self._clear_thumbnails()
            self._update_placeholder()
            self.document_changed.emit(None)
            return
        record = self._records.get(path)
        if record is None:
            return
        self._current = path
        self._current_page = None
        self._populate_thumbnails(path, record)
        self.document_changed.emit(path)

    def _populate_thumbnails(self, path: Path, record: _DocumentRecord) -> None:
        self._clear_thumbnails()
        for idx, pixmap in enumerate(record.thumbnails):
            thumb = PageThumbnail(idx, pixmap, self._thumb_widget)
            thumb.clicked.connect(lambda _, p=path, page=idx: self._on_thumbnail_clicked(p, page))
            self._thumb_layout.addWidget(thumb)
        if record.thumbnails:
            self._current_page = 0
            self._highlight_page(0)
        else:
            self._current_page = None
        self._update_placeholder()

    def _on_thumbnail_clicked(self, path: Path, page_index: int) -> None:
        self._current_page = page_index
        self._highlight_page(page_index)
        self.page_clicked.emit(path, page_index)

    def _highlight_page(self, page_index: int) -> None:
        for i in range(self._thumb_layout.count()):
            item = self._thumb_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, PageThumbnail):
                widget.set_selected(widget.page_index == page_index)
