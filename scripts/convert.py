#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", ".github", "__pycache__", "scripts"}

def lines_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def to_mrs(domains):
    return sorted(set(f'+.{d.lstrip(".")}' for d in domains if d))

def compile_mrs(domains, lst_path: Path):
    if not domains:
        print(f"Skip empty: {lst_path}")
        return

    txt_path = lst_path.with_suffix(".tmp.txt")
    mrs_path = lst_path.with_suffix(".mrs")

    with open(txt_path, "w", encoding="utf-8") as f:
        for d in domains:
            f.write(f"{d}\n")

    try:
        subprocess.run(
            ["mihomo", "convert-ruleset", "domain", "text", str(txt_path), str(mrs_path)],
            check=True,
        )
        print(f"Compiled: {mrs_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        txt_path.unlink(missing_ok=True)

def main():
    for lst_path in ROOT.rglob("*.lst"):
        if any(part in SKIP_DIRS for part in lst_path.parts):
            continue
        domains = to_mrs(lines_from_file(lst_path))
        compile_mrs(domains, lst_path)

if __name__ == "__main__":
    main()
