from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QLineEdit


class ExtractView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("operationView")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.pages = QLineEdit()
        self.pages.setPlaceholderText("Pages to extract, e.g., 1-3,5")
        self.pages.setMinimumHeight(36)
        layout.addWidget(self.pages)

        row = QHBoxLayout()
        self.output_label = QLabel("Output: (choose)")
        self.output_label.setProperty("class", "secondaryText")
        choose = QPushButton("Choose output...")
        choose.setMinimumHeight(36)
        choose.setProperty("class", "secondary")
        choose.clicked.connect(self.choose_output)
        row.addWidget(self.output_label, stretch=1)
        row.addWidget(choose)
        layout.addLayout(row)

        run = QPushButton("Extract Pages from Selected File")
        run.setMinimumHeight(42)
        run.clicked.connect(self.run_extract)
        layout.addWidget(run)
        layout.addStretch(1)

        self._output_path: Path | None = None

    def choose_output(self) -> None:
        out, _ = QFileDialog.getSaveFileName(self, "Save extracted PDF", "extracted.pdf", "PDF (*.pdf)")
        if out:
            self._output_path = Path(out)
            self.output_label.setText(f"Output: {out}")

    def run_extract(self) -> None:
        mw = self.window()
        if mw is None or not hasattr(mw, "selected_file_paths"):
            return
        files = mw.selected_file_paths()
        if not files:
            return
        input_file = files[0]
        if self._output_path is None:
            self.choose_output()
            if self._output_path is None:
                return
        pages = self.pages.text().strip()
        if not pages:
            return
        try:
            processor = mw.processor  # type: ignore[attr-defined]
            mw.start_worker(
                processor.extract_pages,
                input_file,
                self._output_path,
                pages,
                message="Extracting pages...",
            )
        except Exception:
            mw.set_busy(False, "Error during extract")
