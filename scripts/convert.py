#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    ".git",
    "__pycache__",
    "scripts",
}

def normalize_domain(line: str) -> str | None:
    line = line.replace("\r", "")
    if "#" in line:
        line = line.split("#", 1)[0]
    line = line.strip()

    if not line:
        return None

    if line.startswith("+."):
        return line
    if line.startswith("."):
        return f"+{line}"
    return f"+.{line.lstrip('.')}"

def iter_lst_files():
    for path in ROOT.rglob("*.lst"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path

def build_one(lst_path: Path):
    mrs_path = lst_path.with_suffix(".mrs")
    tmp_path = lst_path.with_suffix(".clean.lst")

    seen = set()
    normalized = []

    with lst_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            domain = normalize_domain(raw_line)
            if domain and domain not in seen:
                seen.add(domain)
                normalized.append(domain)

    if not normalized:
        if tmp_path.exists():
            tmp_path.unlink()
        print(f"Skip empty file: {lst_path}")
        return

    normalized.sort()

    with tmp_path.open("w", encoding="utf-8") as f:
        for item in normalized:
            f.write(item + "\n")

    print(f"Converting {lst_path} -> {mrs_path}")
    subprocess.run(
        ["./mihomo", "convert-ruleset", "domain", "text", str(tmp_path), str(mrs_path)],
        check=True,
        cwd=ROOT,
    )

    tmp_path.unlink(missing_ok=True)

def main():
    files = list(iter_lst_files())
    if not files:
        print("No .lst files found")
        return 0

    for file in files:
        build_one(file)

    return 0

if __name__ == "__main__":
    sys.exit(main())
