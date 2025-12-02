from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QFileDialog,
)


class MetadataView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("operationView")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(12)
        form.setHorizontalSpacing(18)
        form.setContentsMargins(0, 0, 0, 0)
        self.title = QLineEdit()
        self.author = QLineEdit()
        self.subject = QLineEdit()
        self.keywords = QLineEdit()
        for field in (self.title, self.author, self.subject, self.keywords):
            field.setMinimumHeight(36)
        form.addRow("Title", self.title)
        form.addRow("Author", self.author)
        form.addRow("Subject", self.subject)
        form.addRow("Keywords", self.keywords)
        layout.addLayout(form)

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

        apply_btn = QPushButton("Apply metadata to Selected File -> New File")
        apply_btn.setMinimumHeight(42)
        apply_btn.clicked.connect(self.apply_metadata)
        layout.addWidget(apply_btn)
        layout.addStretch(1)

        self._output_path: Path | None = None

    def choose_output(self) -> None:
        out, _ = QFileDialog.getSaveFileName(self, "Save PDF with metadata", "with_metadata.pdf", "PDF (*.pdf)")
        if out:
            self._output_path = Path(out)
            self.output_label.setText(f"Output: {out}")

    def apply_metadata(self) -> None:
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
        try:
            processor = mw.processor  # type: ignore[attr-defined]
            mw.start_worker(
                processor.write_metadata,
                input_file,
                self._output_path,
                self.title.text().strip() or None,
                self.author.text().strip() or None,
                self.subject.text().strip() or None,
                self.keywords.text().strip() or None,
                message="Writing metadata...",
            )
        except Exception:
            mw.set_busy(False, "Error during metadata write")
