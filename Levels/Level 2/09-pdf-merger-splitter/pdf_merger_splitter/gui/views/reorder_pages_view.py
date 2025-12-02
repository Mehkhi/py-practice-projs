from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFileDialog


class ReorderPagesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("operationView")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        instruction = QLabel("Enter new page order (e.g., 3,1,2-4):")
        instruction.setProperty("class", "secondaryText")
        layout.addWidget(instruction)
        self.order = QLineEdit()
        self.order.setMinimumHeight(36)
        layout.addWidget(self.order)

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

        apply_btn = QPushButton("Apply Order to Selected File")
        apply_btn.setMinimumHeight(42)
        apply_btn.clicked.connect(self.apply_order)
        layout.addWidget(apply_btn)
        layout.addStretch(1)

        self._output_path: Path | None = None

    def choose_output(self) -> None:
        out, _ = QFileDialog.getSaveFileName(self, "Save reordered PDF", "reordered.pdf", "PDF (*.pdf)")
        if out:
            self._output_path = Path(out)
            self.output_label.setText(f"Output: {out}")

    def apply_order(self) -> None:
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
        order_str = self.order.text().strip()
        if not order_str:
            return
        try:
            processor = mw.processor  # type: ignore[attr-defined]
            mw.start_worker(
                processor.reorder_pages,
                input_file,
                self._output_path,
                order_str,
                message="Reordering pages...",
            )
        except Exception:
            mw.set_busy(False, "Error during reorder")
