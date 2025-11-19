#!/usr/bin/env python3
"""Render a quick analog preview for sanity checks.

Example:
    python scripts/render_preview.py --env fluvial --seed 12
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analog_image_generator import preview


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--env",
        choices=preview.ENVIRONMENTS,
        default="fluvial",
        help="Environment tag to render",
    )
    parser.add_argument(
        "--style",
        help="Optional style (meandering|braided|anastomosing) forwarded to generate_fluvial",
    )
    parser.add_argument("--seed", type=int, default=0, help="Seed for deterministic previews")
    parser.add_argument("--width", type=int, default=512, help="Preview width in pixels")
    parser.add_argument("--height", type=int, default=512, help="Preview height in pixels")
    parser.add_argument(
        "--params-file",
        type=Path,
        help="Optional JSON file with custom generator parameters",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist/previews"),
        help="Directory where preview artifacts will be written",
    )
    parser.add_argument("--slug", help="Optional slug for output filenames")
    parser.add_argument(
        "--skip-masks",
        action="store_true",
        help="Do not persist mask rasters (still tracked in metadata)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    params: dict[str, Any] | None = None
    if args.params_file:
        params = json.loads(args.params_file.read_text())
    if args.style:
        if params is None:
            params = {}
        params["style"] = args.style

    analog, masks, metadata = preview.generate_preview(
        args.env,
        width=args.width,
        height=args.height,
        seed=args.seed,
        params=params,
    )

    if args.skip_masks:
        masks = {}

    artifacts = preview.save_preview(
        analog,
        masks,
        metadata,
        output_dir=args.output_dir,
        slug=args.slug,
    )

    summary = {
        "env": args.env,
        "seed": args.seed,
        "analog": str(artifacts.analog_path),
        "metadata": str(artifacts.metadata_path),
        "mask_count": len(artifacts.mask_paths),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
