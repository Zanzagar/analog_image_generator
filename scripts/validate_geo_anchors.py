#!/usr/bin/env python3
"""Validate GEOLOGIC_RULES code + notebook anchors."""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from typing import Iterable

import nbformat
from nbformat import validator

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "GEOLOGIC_RULES.md"


def _load_notebook_ids() -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {}
    for nb_path in (ROOT / "notebooks").glob("*.ipynb"):
        nb = nbformat.read(nb_path, as_version=4)
        validator.normalize(nb)
        anchors = {
            cell.get("metadata", {}).get("id")
            for cell in nb.get("cells", [])
            if isinstance(cell, dict)
        }
        ids[str(nb_path.resolve())] = {anchor for anchor in anchors if anchor}
    return ids


TARGET_ENVS = {"Meandering", "Braided", "Anastomosing", "Stacked", "Fluvial", "All"}


def _parse_geo_rows() -> list[tuple[list[str], list[str]]]:
    rows: list[tuple[list[str], list[str]]] = []
    pattern = re.compile(r"`([^`]+)`")
    with DOC.open() as fh:
        for line in fh:
            if "analog_image_generator." not in line:
                continue
            parts = [part.strip() for part in line.strip().split("|")]
            if len(parts) < 4 or parts[0] not in TARGET_ENVS:
                continue
            matches = pattern.findall(line)
            if len(matches) < 2:
                continue
            code_tokens = matches[:-1]
            notebook_token = matches[-1]
            code_anchors = [part.strip() for part in " / ".join(code_tokens).split(" / ")]
            notebook_entries = []
            for entry in notebook_token.split(" / "):
                entry = entry.strip()
                if "#" not in entry:
                    continue
                notebook_rel = entry.split("#", 1)[0]
                if not (ROOT / notebook_rel).exists():
                    continue
                notebook_entries.append(entry)
            if not notebook_entries:
                continue
            rows.append(
                (
                    [entry for entry in code_anchors if entry],
                    notebook_entries,
                )
            )
    return rows


def _check_callable(anchor: str) -> str | None:
    func_path = anchor.split("(")[0].strip()
    if not func_path:
        return f"Empty anchor in code column: {anchor}"
    if "aeolian" in func_path or "estuarine" in func_path:
        return None
    try:
        module_name, attr_name = func_path.rsplit(".", 1)
    except ValueError:
        return f"Unable to parse anchor: {anchor}"
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:  # pragma: no cover
        return f"Import failed for {module_name}: {exc}"
    if not hasattr(module, attr_name):
        return f"{module_name} missing attribute {attr_name}"
    return None


def _check_notebook_anchor(entry: str, notebook_ids: dict[str, set[str]]) -> str | None:
    if "#" not in entry:
        return f"Notebook anchor missing '#': {entry}"
    notebook_rel, anchor = entry.split("#", 1)
    notebook_file = (ROOT / notebook_rel)
    if not notebook_file.exists():
        return None
    notebook_path = str(notebook_file.resolve())
    if notebook_path not in notebook_ids:
        return f"Notebook {notebook_rel} not found for anchor {entry}"
    if anchor not in notebook_ids[notebook_path]:
        return f"Anchor id {anchor} missing in {notebook_rel}"
    return None


def main() -> int:
    notebook_ids = _load_notebook_ids()
    rows = _parse_geo_rows()
    issues: list[str] = []
    for code_anchors, notebook_entries in rows:
        for code_anchor in code_anchors:
            err = _check_callable(code_anchor)
            if err:
                issues.append(err)
        for entry in notebook_entries:
            err = _check_notebook_anchor(entry, notebook_ids)
            if err:
                issues.append(err)
    if issues:
        for issue in issues:
            print(f"[GEOLOGIC_RULES] {issue}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
