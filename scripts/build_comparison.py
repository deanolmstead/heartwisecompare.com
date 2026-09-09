#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from page_factory import ROOT, build_comparison, load_data


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one Heartwise comparison and synchronize its discovery surfaces.")
    parser.add_argument("data", type=Path, help="Structured comparison JSON file")
    parser.add_argument("--root", type=Path, default=ROOT, help="Heartwise site root")
    parser.add_argument("--check", action="store_true", help="Exit nonzero when generated files would change")
    args = parser.parse_args()

    data = load_data(args.data)
    changed = build_comparison(args.root.resolve(), data, check=args.check)
    if args.check:
        if changed:
            print(f"drift: {data['slug']} needs regeneration")
            return 1
        print(f"clean: {data['slug']} matches generated output")
        return 0
    print(f"{'updated' if changed else 'unchanged'}: {data['slug']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
