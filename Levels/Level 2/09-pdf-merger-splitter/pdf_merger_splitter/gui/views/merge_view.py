from __future__ import annotations

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QCheckBox,
    QLabel,
    QMessageBox,
)


class MergeView(QWidget):
    """Merge operation UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("operationView")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self.preserve_metadata = QCheckBox("Preserve metadata from first file")
        self.preserve_metadata.setChecked(True)
        layout.addWidget(self.preserve_metadata)

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

        run = QPushButton("Merge Selected Files")
        run.setMinimumHeight(42)
        run.clicked.connect(self.run_merge)
        layout.addWidget(run)

        layout.addStretch(1)

        self._output_path: Path | None = None

    def choose_output(self) -> None:
        out, _ = QFileDialog.getSaveFileName(self, "Save merged PDF", "merged.pdf", "PDF (*.pdf)")
        if out:
            self._output_path = Path(out)
            self.output_label.setText(f"Output: {out}")

    def run_merge(self) -> None:
        mw = self.window()
        if mw is None or not hasattr(mw, "selected_file_paths"):
            return
        files = mw.selected_file_paths()
        if not files:
            QMessageBox.warning(self, "No files selected", "Add at least one PDF to merge.")
            return
        if self._output_path is None:
            self.choose_output()
            if self._output_path is None:
                QMessageBox.information(
                    self,
                    "Merge cancelled",
                    "No output file chosen; merge cancelled.",
                )
                return

        # Defer to main window to run worker with processor
        try:
            processor = mw.processor  # type: ignore[attr-defined]
            mw.start_worker(
                processor.merge_pdfs,
                files,
                self._output_path,
                self.preserve_metadata.isChecked(),
                message="Merging files...",
                on_success=lambda _result, total=len(files), target=self._output_path: (
                    f"Merged {total} file(s) into {target}"
                ),
            )
        except Exception:
            mw.set_busy(False, "Error during merge")
