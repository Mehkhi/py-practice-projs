from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import logging
from PySide6.QtCore import Qt, QThreadPool, QSettings, QStandardPaths, QUrl
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QWidget,
)
from PySide6.QtGui import QAction
from PySide6.QtGui import QDesktopServices
from .theme import apply_dark_palette, apply_light_palette

from ..core import PDFProcessor
from .pdf_preview_widget import PDFPreviewWidget
from .views.merge_view import MergeView
from .views.split_view import SplitView
from .views.rotate_view import RotateView
from .views.extract_view import ExtractView
from .views.reorder_pages_view import ReorderPagesView
from .views.metadata_view import MetadataView
from .views.settings_view import SettingsView


class MainWindow(QMainWindow):
    """Main window shell for the PDF Split desktop application."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Split")
        self.setMinimumSize(900, 600)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.processor = PDFProcessor()
        self.thread_pool = QThreadPool.globalInstance()
        self.current_worker = None
        self._pending_success_message: str | None = None
        self._pending_success_callback: Callable[[Any], None] | None = None
        self._progress_dialog = None
        self.logger = logging.getLogger(__name__)
        self.settings_view: SettingsView | None = None

        # Settings
        self.settings = QSettings("PDF Split", "PDF Split")

        # Central layout: splitter with file list (left) and tabs (right)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(4)
        self.preview = PDFPreviewWidget()
        self.preview.files_dropped.connect(self._handle_dropped_files)
        self.preview.document_changed.connect(self._on_document_changed)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabBarAutoHide(False)
        self.tabs.setElideMode(Qt.ElideRight)

        self.splitter.addWidget(self.preview)
        self.splitter.addWidget(self.tabs)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        self.setCentralWidget(self.splitter)

        # Tabs (placeholders for now)
        self._init_tabs()

        # Status bar with progress bar and status label
        self.status_bar = QStatusBar()
        self.status_bar.setContentsMargins(12, 0, 12, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate by default
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.status_label = QLabel("Ready")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setVisible(False)
        self.cancel_button.setProperty("class", "secondary")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)

        self.status_bar.addPermanentWidget(self.progress_bar, stretch=0)
        self.status_bar.addPermanentWidget(self.cancel_button, stretch=0)
        self.status_bar.addWidget(self.status_label, stretch=1)
        self.setStatusBar(self.status_bar)

        # Menus
        self._init_menus()
        self._init_toolbar()

    # ---- UI init helpers ----
    def _init_tabs(self) -> None:
        self.tabs.addTab(MergeView(parent=self), "Merge")
        self.tabs.addTab(SplitView(parent=self), "Split")
        self.tabs.addTab(RotateView(parent=self), "Rotate")
        self.tabs.addTab(ExtractView(parent=self), "Extract")
        self.tabs.addTab(ReorderPagesView(parent=self), "Reorder Pages")
        self.tabs.addTab(MetadataView(parent=self), "Metadata")
        self.settings_view = SettingsView(parent=self)
        self.settings_view.theme_requested.connect(self._on_theme_requested)
        self.settings_view.sync_theme(self.settings.value("darkMode", False, type=bool))
        self.tabs.addTab(self.settings_view, "Settings")

    def _init_menus(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        self.act_add_files = QAction("Add Files...", self)
        self.act_add_files.triggered.connect(self.action_add_files)
        file_menu.addAction(self.act_add_files)

        self.act_add_folder = QAction("Add Folder...", self)
        self.act_add_folder.triggered.connect(self.action_add_folder)
        file_menu.addAction(self.act_add_folder)
        file_menu.addSeparator()
        self.act_clear_list = QAction("Clear List", self)
        self.act_clear_list.triggered.connect(self._clear_documents)
        file_menu.addAction(self.act_clear_list)
        file_menu.addSeparator()
        self.act_exit = QAction("Exit", self)
        self.act_exit.triggered.connect(self.close)
        file_menu.addAction(self.act_exit)

        help_menu = menubar.addMenu("&Help")
        self.act_about = QAction("About", self)
        self.act_about.triggered.connect(self.action_about)
        help_menu.addAction(self.act_about)

        self.act_open_logs = QAction("Open Logs Folder", self)
        self.act_open_logs.triggered.connect(self.action_open_logs)
        help_menu.addAction(self.act_open_logs)

        view_menu = menubar.addMenu("&View")
        self.act_dark = QAction("Dark Mode", self, checkable=True)
        self.act_dark.setChecked(self.settings.value("darkMode", False, type=bool))
        self.act_dark.toggled.connect(self.toggle_dark_mode)
        view_menu.addAction(self.act_dark)
        if self.settings_view is not None:
            self.settings_view.sync_theme(self.act_dark.isChecked())

    def _init_toolbar(self) -> None:
        toolbar = QToolBar("File Actions", self)
        toolbar.setObjectName("fileActionsToolBar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        toolbar.addAction(self.act_add_files)
        toolbar.addAction(self.act_add_folder)
        toolbar.addSeparator()
        toolbar.addAction(self.act_clear_list)
        self.addToolBar(toolbar)

    # ---- Actions ----
    def action_add_files(self) -> None:
        start_dir = self._last_dir() or ""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF files",
            start_dir,
            "PDF Files (*.pdf)",
        )
        if files:
            paths = [Path(f) for f in files]
            added = self.preview.add_documents(paths)
            if added:
                self._remember_dir(added[-1].parent)

    def action_add_folder(self) -> None:
        start_dir = self._last_dir() or ""
        folder = QFileDialog.getExistingDirectory(self, "Select folder with PDFs", start_dir)
        if folder:
            p = Path(folder)
            pdfs = sorted(pp for pp in p.glob("*.pdf"))
            added = self.preview.add_documents(pdfs)
            if added:
                self._remember_dir(p)

    def action_about(self) -> None:
        QMessageBox.information(
            self,
            "About PDF Split",
            "PDF Split\nA desktop GUI for merging, splitting, and editing PDFs.",
        )

    def action_open_logs(self) -> None:
        log_dir = self._log_dir()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(log_dir)))

    # ---- Helpers ----
    def set_busy(self, busy: bool, message: str | None = None) -> None:
        self.progress_bar.setVisible(busy)
        self.cancel_button.setVisible(busy)
        self.cancel_button.setEnabled(busy)
        self.status_label.setText(message or ("Working..." if busy else "Ready"))
        self._set_progress_dialog_visible(busy, message or "Working...")
        self.splitter.setEnabled(not busy)

    def selected_file_paths(self) -> list[Path]:
        documents = self.preview.document_paths()
        if not documents:
            return []
        current = self.preview.current_document()
        if current is None:
            return documents
        rest = [p for p in documents if p != current]
        return [current, *rest]

    # ---- Worker handling ----
    def start_worker(
        self,
        func,
        *args,
        message: str = "Working...",
        success_message: str | None = None,
        on_success: Callable[[Any], None] | None = None,
        **kwargs,
    ) -> None:
        from .workers import FunctionWorker

        if self.current_worker is not None:
            QMessageBox.warning(self, "Busy", "An operation is already running.")
            return
        self.set_busy(True, message)
        self._pending_success_message = success_message
        self._pending_success_callback = on_success
        worker = FunctionWorker(func, *args, **kwargs)
        worker.signals.started.connect(lambda: self.logger.debug("Worker started"))
        worker.signals.error.connect(self._on_worker_error)
        worker.signals.finished.connect(self._on_worker_finished)
        self.current_worker = worker
        self.thread_pool.start(worker)

    def _on_worker_error(self, msg: str) -> None:
        self.logger.error("Operation failed: %s", msg)
        QMessageBox.critical(self, "Error", msg)
        self.set_busy(False, "Ready")
        self.current_worker = None
        self._pending_success_message = None
        self._pending_success_callback = None

    def _on_worker_finished(self, result) -> None:
        callback = self._pending_success_callback
        message = self._pending_success_message
        self._pending_success_callback = None
        self._pending_success_message = None
        self.current_worker = None

        callback_message: str | None = None
        if callback is not None:
            try:
                returned = callback(result)
                if isinstance(returned, str):
                    callback_message = returned
            except Exception as exc:  # noqa: BLE001
                self._on_worker_error(str(exc))
                return

        final_message = callback_message or message
        self.set_busy(False, final_message or "Ready")
        if final_message:
            QMessageBox.information(self, "Success", final_message)

    def _on_cancel_clicked(self) -> None:
        # Cooperative cancel placeholder: we cannot force-stop QRunnable safely.
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Cancel requested (will complete asap)...")

    # ---- Settings helpers ----
    def _last_dir(self) -> str | None:
        return self.settings.value("lastDir", type=str)

    def _remember_dir(self, path: Path) -> None:
        self.settings.setValue("lastDir", str(path))

    def _log_dir(self) -> Path:
        base = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) or ".")
        base.mkdir(parents=True, exist_ok=True)
        return base

    def closeEvent(self, event) -> None:  # noqa: D401
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("darkMode", self.act_dark.isChecked())
        self.settings.sync()
        super().closeEvent(event)

    # ---- Theme ----
    def showEvent(self, event) -> None:  # noqa: D401
        super().showEvent(event)
        # restore geometry/state once on first show
        geom = self.settings.value("geometry")
        state = self.settings.value("windowState")
        if geom is not None:
            self.restoreGeometry(geom)
        if state is not None:
            self.restoreState(state)
        # apply theme
        self.toggle_dark_mode(self.act_dark.isChecked())

    def toggle_dark_mode(self, enabled: bool) -> None:
        from PySide6.QtWidgets import QApplication

        qapp = QApplication.instance()
        if qapp is None:
            return
        qapp.setStyle("Fusion")
        if enabled:
            apply_dark_palette(qapp)
        else:
            apply_light_palette(qapp)
        if self.settings_view is not None:
            self.settings_view.sync_theme(enabled)

    # ---- Internal helpers ----
    def _handle_dropped_files(self, paths: list[Path]) -> None:
        added = self.preview.add_documents(paths)
        if added:
            self._remember_dir(added[-1].parent)

    def _on_document_changed(self, path: Path | None) -> None:
        if not path:
            self.status_label.setText("Ready")
        else:
            self.status_label.setText(f"Selected: {path.name}")

    def _clear_documents(self) -> None:
        self.preview.clear()
        self.status_label.setText("Ready")

    def _set_progress_dialog_visible(self, visible: bool, message: str) -> None:
        from PySide6.QtWidgets import QProgressDialog

        if visible:
            if self._progress_dialog is None:
                self._progress_dialog = QProgressDialog(self)
                self._progress_dialog.setWindowTitle("Processing")
                self._progress_dialog.setCancelButton(None)
                self._progress_dialog.setMinimum(0)
                self._progress_dialog.setMaximum(0)
                self._progress_dialog.setWindowModality(Qt.ApplicationModal)
            self._progress_dialog.setLabelText(message)
            self._progress_dialog.show()
        else:
            if self._progress_dialog is not None:
                self._progress_dialog.hide()

    def _on_theme_requested(self, dark_mode: bool) -> None:
        if self.act_dark.isChecked() == dark_mode:
            self.toggle_dark_mode(dark_mode)
            return
        self.act_dark.setChecked(dark_mode)
