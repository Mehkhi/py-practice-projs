from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QFileDialog,
)


class RotateView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("operationView")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        row = QHBoxLayout()
        row.addWidget(QLabel("Rotation:"))
        self.rotation = QComboBox()
        self.rotation.addItems(["90", "180", "270"])
        self.rotation.setMinimumHeight(36)
        row.addWidget(self.rotation)
        layout.addLayout(row)

        self.pages = QLineEdit()
        self.pages.setPlaceholderText("Page range, e.g., 1-3,5 (leave empty for all)")
        layout.addWidget(self.pages)

        out_row = QHBoxLayout()
        self.output_label = QLabel("Output: (choose)")
        self.output_label.setProperty("class", "secondaryText")
        choose = QPushButton("Choose output...")
        choose.setMinimumHeight(36)
        choose.setProperty("class", "secondary")
        choose.clicked.connect(self.choose_output)
        out_row.addWidget(self.output_label, stretch=1)
        out_row.addWidget(choose)
        layout.addLayout(out_row)

        run = QPushButton("Rotate Selected File")
        run.setMinimumHeight(42)
        run.clicked.connect(self.run_rotate)
        layout.addWidget(run)
        layout.addStretch(1)

        self._output_path: Path | None = None

    def choose_output(self) -> None:
        out, _ = QFileDialog.getSaveFileName(self, "Save rotated PDF", "rotated.pdf", "PDF (*.pdf)")
        if out:
            self._output_path = Path(out)
            self.output_label.setText(f"Output: {out}")

    def run_rotate(self) -> None:
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
        pages = self.pages.text().strip() or None
        rotation = int(self.rotation.currentText())

        try:
            processor = mw.processor  # type: ignore[attr-defined]
            mw.start_worker(
                processor.rotate_pages,
                input_file,
                self._output_path,
                rotation,
                pages,
                message="Rotating file...",
            )
        except Exception:
            mw.set_busy(False, "Error during rotate")
