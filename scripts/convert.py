#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent

SKIP_PARTS = {
    ".git",
    ".github",
    "__pycache__",
    "scripts",
}

def lines_from_file(filepath: Path):
    if not filepath.exists():
        return []

    result = []
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.replace("\r", "")
            line = line.split("#", 1)[0].strip()
            if line:
                result.append(line)
    return result

def to_mrs(domains):
    out = []
    seen = set()

    for d in domains:
        d = d.strip()
        if not d:
            continue

        if d.startswith("+."):
            value = d
        elif d.startswith("."):
            value = f"+{d}"
        else:
            value = f"+.{d.lstrip('.')}"

        if value not in seen:
            seen.add(value)
            out.append(value)

    return sorted(out)

def iter_lst_files():
    for path in ROOT.rglob("*.lst"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path

def compile_mrs(domains, lst_path: Path):
    if not domains:
        print(f"Skip empty file: {lst_path}")
        return

    txt_path = lst_path.with_suffix(".tmp.txt")
    mrs_path = lst_path.with_suffix(".mrs")

    with txt_path.open("w", encoding="utf-8") as f:
        for d in domains:
            f.write(f"{d}\n")

    try:
        subprocess.run(
            ["./mihomo", "convert-ruleset", "domain", "text", str(txt_path), str(mrs_path)],
            check=True,
            cwd=ROOT,
        )
        print(f"Compiled: {mrs_path}")
    finally:
        txt_path.unlink(missing_ok=True)

def main():
    files = list(iter_lst_files())

    if not files:
        print("No .lst files found")
        return 0

    for lst_path in files:
        domains = lines_from_file(lst_path)
        mrs_domains = to_mrs(domains)
        compile_mrs(mrs_domains, lst_path)

    return 0

if __name__ == "__main__":
    sys.exit(main())
