"""Lightweight mod loader for merging custom content packs."""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .logging_utils import log_warning


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
        self.mods_path = mods_path
        self.enabled = enabled
        self.manifests: List[ModManifest] = []

    def discover_mods(self) -> List[ModManifest]:
        """Load all mod manifests from the mods directory."""
        self.manifests.clear()
        if not self.enabled:
            return self.manifests

        if not os.path.isdir(self.mods_path):
            return self.manifests

        for entry in os.listdir(self.mods_path):
            mod_dir = os.path.join(self.mods_path, entry)
            if not os.path.isdir(mod_dir):
                continue

            manifest_path = os.path.join(mod_dir, "mod.json")
            if not os.path.exists(manifest_path):
                manifest_path = os.path.join(mod_dir, "manifest.json")
                if not os.path.exists(manifest_path):
                    continue

            manifest_data = self._load_json(manifest_path, context="mod manifest")
            if not manifest_data:
                continue

            manifest = ModManifest.from_dict(manifest_data, manifest_path)
            if manifest:
                self.manifests.append(manifest)
        return self.manifests

    def merge_data(self, base_path: str, data_key: str) -> Dict[str, Any]:
        """
        Merge base JSON data with any mod-provided overrides.

        Mods can specify `{ "data_overrides": { "<data_key>": "relative/path.json" } }`
        in their manifest. Lists are concatenated, dictionaries are merged
        recursively, and scalar values overwrite base values.
        """
        base_data = self._load_json(base_path, context=f"{data_key} (base)")
        merged: Dict[str, Any] = dict(base_data)

        for manifest in self.manifests:
            if not manifest.enabled:
                continue

            override_rel = manifest.data_overrides.get(data_key)
            if not override_rel:
                continue

            override_path = os.path.join(manifest.base_path, override_rel)
            if not os.path.exists(override_path):
                log_warning(f"Mod {manifest.mod_id} missing override file for {data_key}: {override_path}")
                continue

            override_data = self._load_json(override_path, context=f"{data_key} override for {manifest.mod_id}")
            if override_data:
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

    def _load_json(self, path: str, context: str = "mod data") -> Dict[str, Any]:
        """Load a JSON file with graceful degradation."""
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r") as handle:
                return json.load(handle)
        except Exception as exc:
            log_warning(f"Failed to load {context} from {path}: {exc}")
            return {}
