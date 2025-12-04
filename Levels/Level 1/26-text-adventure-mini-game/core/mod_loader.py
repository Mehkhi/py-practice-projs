"""Lightweight mod loader for merging custom content packs."""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .logging_utils import log_schema_warning, log_warning
from .path_validation import (
    ensure_directory_exists,
    sanitize_filename,
    validate_path_inside_base,
)


@dataclass
class ModManifest:
    """Structured manifest describing a mod's metadata and content paths."""

    mod_id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    entry_point: Optional[str] = None
    data_overrides: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    base_path: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any], manifest_path: str) -> Optional["ModManifest"]:
        """Create a manifest from a raw dictionary, validating required fields."""
        required_fields = ("id", "name", "version")
        if not all(field in data for field in required_fields):
            log_warning(f"Skipping mod manifest {manifest_path}: missing required fields")
            return None

        overrides = data.get("data_overrides", {})
        if not isinstance(overrides, dict):
            overrides = {}

        manifest = cls(
            mod_id=str(data["id"]),
            name=str(data["name"]),
            version=str(data["version"]),
            description=str(data.get("description", "")),
            author=str(data.get("author", "")),
            entry_point=data.get("entry_point"),
            data_overrides={str(k): str(v) for k, v in overrides.items()},
            enabled=bool(data.get("enabled", True)),
            base_path=os.path.dirname(manifest_path),
        )
        return manifest


class ModLoader:
    """Discovers and merges mods from a `mods/` directory."""

    def __init__(self, mods_path: str = "mods", enabled: bool = True):
        """Initialize ModLoader.

        Args:
            mods_path: Base directory containing mods
            enabled: Whether mod loading is enabled

        Raises:
            ValueError: If mods_path is invalid
        """
        # Validate and resolve mods directory
        success, resolved_path = ensure_directory_exists(mods_path, create_if_missing=False)
        if not success or not resolved_path:
            # If directory doesn't exist and can't be created, that's OK - just log
            # We'll check again when discovering mods
            resolved_path = os.path.abspath(mods_path)
        self.mods_path = resolved_path
        self.enabled = enabled
        self.manifests: List[ModManifest] = []

    def discover_mods(self) -> List[ModManifest]:
        """Load all mod manifests from the mods directory."""
        self.manifests.clear()
        if not self.enabled:
            return self.manifests

        if not os.path.isdir(self.mods_path):
            return self.manifests

        try:
            entries = os.listdir(self.mods_path)
        except (OSError, PermissionError):
            log_warning(f"Cannot access mods directory: {self.mods_path}")
            return self.manifests

        for entry in sorted(entries):
            # Sanitize directory name to prevent path traversal
            sanitized_entry = sanitize_filename(entry)
            if not sanitized_entry or sanitized_entry != entry:
                log_warning(f"Skipping mod directory with invalid name: {entry}")
                continue

            # Validate mod directory path stays within mods_path
            is_valid, mod_dir = validate_path_inside_base(
                entry, self.mods_path, allow_absolute=False
            )
            if not is_valid or not mod_dir or not os.path.isdir(mod_dir):
                continue

            # Check for mod.json or manifest.json
            for manifest_filename in ["mod.json", "manifest.json"]:
                is_valid_manifest, manifest_path = validate_path_inside_base(
                    manifest_filename, mod_dir, allow_absolute=False
                )
                if is_valid_manifest and manifest_path and os.path.exists(manifest_path):
                    manifest_data = self._load_json(manifest_path, context="mod manifest")
                    if not manifest_data:
                        continue

                    manifest = ModManifest.from_dict(manifest_data, manifest_path)
                    if manifest:
                        self.manifests.append(manifest)
                    break  # Found manifest, move to next mod
        return self.manifests

    def merge_data(self, base_path: str, data_key: str) -> Dict[str, Any]:
        """
        Merge base JSON data with any mod-provided overrides.

        Mods can specify `{ "data_overrides": { "<data_key>": "relative/path.json" } }`
        in their manifest. Lists are concatenated, dictionaries are merged
        recursively, and scalar values overwrite base values.
        """
        context = "mod loader"
        base_data = self._load_json(base_path, context=f"{data_key} (base)")
        if not isinstance(base_data, dict):
            log_schema_warning(
                context,
                f"expected dict for base '{data_key}', got {type(base_data).__name__}; treating as empty object",
                section="base",
                identifier=data_key,
            )
            base_data = {}

        merged: Dict[str, Any] = dict(base_data)

        for manifest in self.manifests:
            if not manifest.enabled:
                continue

            override_rel = manifest.data_overrides.get(data_key)
            if not override_rel:
                continue

            # Validate override path stays within mod directory
            is_valid, override_path = validate_path_inside_base(
                override_rel, manifest.base_path, allow_absolute=False
            )
            if not is_valid or not override_path:
                log_warning(
                    f"Mod {manifest.mod_id} has invalid override path for {data_key}: {override_rel}"
                )
                continue

            if not os.path.exists(override_path):
                log_warning(f"Mod {manifest.mod_id} missing override file for {data_key}: {override_path}")
                continue

            override_data = self._load_json(override_path, context=f"{data_key} override for {manifest.mod_id}")
            if not override_data:
                continue
            if not isinstance(override_data, dict):
                log_schema_warning(
                    context,
                    f"expected dict override for '{data_key}', got {type(override_data).__name__}; skipping {manifest.mod_id}",
                    section="override",
                    identifier=manifest.mod_id,
                )
                continue
            merged = self._merge_payload(merged, override_data)

        return merged

    def _merge_payload(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge dictionaries, concatenating lists when possible."""
        merged = dict(base)
        for key, value in overlay.items():
            if isinstance(value, list):
                existing_list = merged.get(key, [])
                if isinstance(existing_list, list):
                    merged[key] = existing_list + value
                else:
                    merged[key] = list(value)
            elif isinstance(value, dict):
                existing_dict = merged.get(key, {})
                if isinstance(existing_dict, dict):
                    merged[key] = self._merge_payload(existing_dict, value)
                else:
                    merged[key] = dict(value)
            else:
                merged[key] = value
        return merged

    def _load_json(self, path: str, context: str = "mod data") -> Any:
        """Load a JSON file with graceful degradation.

        Path should already be validated before calling this method.
        """
        if not path or not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, PermissionError) as exc:
            log_warning(f"Failed to load {context} from {path}: {exc}")
            return {}
        except json.JSONDecodeError as exc:
            log_warning(f"Invalid JSON in {context} at {path}: {exc}")
            return {}
        except Exception as exc:
            log_warning(f"Unexpected error loading {context} from {path}: {exc}")
            return {}
