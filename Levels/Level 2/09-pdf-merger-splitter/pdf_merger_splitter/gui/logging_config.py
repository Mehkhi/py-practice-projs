from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import sys
try:
    from PySide6.QtCore import QStandardPaths  # type: ignore[reportMissingImports]
except Exception:  # PySide6 may not be installed in non-GUI environments
    QStandardPaths = None  # type: ignore[assignment]


def init_logging(app_name: str = "PDF Split") -> Path:
    """Initialize rotating file logging under the OS app data location.

    Returns the directory used for logs.
    """
    if QStandardPaths is not None:
        base_path_str = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) or "."
        log_dir = Path(base_path_str)
    else:
        # Fallback locations when PySide6 is unavailable
        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA") or (Path.home() / "AppData" / "Roaming"))
            log_dir = base / app_name
        elif sys.platform == "darwin":
            log_dir = Path.home() / "Library" / "Application Support" / app_name
        else:
            base = Path(os.getenv("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
            log_dir = base / app_name
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    handler = RotatingFileHandler(str(log_file), maxBytes=1_000_000, backupCount=5)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    root = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        root.addHandler(handler)
    if root.level == logging.WARNING:
        root.setLevel(logging.INFO)

    logging.getLogger(__name__).info("Logging initialized at %s", log_file)
    return log_dir
