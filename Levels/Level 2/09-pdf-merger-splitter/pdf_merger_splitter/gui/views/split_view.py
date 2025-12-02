from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QLineEdit,
    QMessageBox,
)


class SplitView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("operationView")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        row = QHBoxLayout()
        self.output_label = QLabel("Output dir: (choose)")
        self.output_label.setProperty("class", "secondaryText")
        choose = QPushButton("Choose output dir...")
        choose.setMinimumHeight(36)
        choose.setProperty("class", "secondary")
        choose.clicked.connect(self.choose_output_dir)
        row.addWidget(self.output_label, stretch=1)
        row.addWidget(choose)
        layout.addLayout(row)

        self.ranges = QLineEdit()
        self.ranges.setPlaceholderText("Ranges like 1-3,5 or leave empty for each page")
        self.ranges.returnPressed.connect(self.run_split)
        layout.addWidget(self.ranges)

        run = QPushButton("Split Selected File")
        run.setAutoDefault(True)
        run.setDefault(True)
        run.setMinimumHeight(42)
        run.clicked.connect(self.run_split)
        layout.addWidget(run)
        layout.addStretch(1)

        self._output_dir: Path | None = None

    def choose_output_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder")
        if folder:
            self._output_dir = Path(folder)
            self.output_label.setText(f"Output dir: {folder}")

    def run_split(self) -> None:
        mw = self.window()
        if mw is None or not hasattr(mw, "selected_file_paths"):
            return
        files = mw.selected_file_paths()
        if not files:
            QMessageBox.warning(self, "No file selected", "Select a PDF in the file list to split.")
            return
        input_file = files[0]
        if self._output_dir is None:
            self.choose_output_dir()
            if self._output_dir is None:
                QMessageBox.information(
                    self,
                    "Split cancelled",
                    "No output folder chosen; split cancelled.",
                )
                return
        ranges_text = self.ranges.text().strip()
        ranges = [s.strip() for s in ranges_text.split(',') if s.strip()] if ranges_text else None

        try:
            processor = mw.processor  # type: ignore[attr-defined]
            mw.start_worker(
                processor.split_pdf,
                input_file,
                self._output_dir,
                ranges,
                message="Splitting file...",
                on_success=lambda result, name=input_file.name, out_dir=self._output_dir: self._format_split_success(
                    result, name, out_dir
                ),
            )
        except Exception:
            mw.set_busy(False, "Error during split")

    def _format_split_success(self, result, name: str, out_dir: Path) -> str:
        if isinstance(result, list):
            count = len(result)
        else:
            count = 0
        if count == 0:
            return f"No new PDFs were created for '{name}'. Check the output folder {out_dir}."
        return f"Split '{name}' into {count} file(s) in {out_dir}"
