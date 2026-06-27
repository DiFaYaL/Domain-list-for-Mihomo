#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {".git", ".github", "__pycache__", "scripts"}


def clean_and_sort_domains(domains: list[str]) -> list[str]:
    """Очищает строки от пробелов, лишних префиксов, комментариев и дубликатов."""
    clean_set = set()
    for d in domains:
        d = d.strip()
        if not d or d.startswith("#"):
            continue
        if d.startswith("DOMAIN-SUFFIX,"):
            d = d[len("DOMAIN-SUFFIX,"):]
        if d.startswith("+."):
            d = d[2:]
        elif d.startswith("."):
            d = d[1:]
        if d:
            clean_set.add(d.lower())
    return sorted(clean_set)


def lines_from_file(filepath: Path) -> list[str]:
    """Читает строки файла, убирает inline-комментарии и пустые строки."""
    if not filepath.exists():
        return []
    result = []
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.replace("\r", "").replace("\n", "")
            if "#" in line:
                line = line.split("#", 1)[0]
            line = line.strip()
            if line:
                result.append(line)
    return result


def generate_all_formats(raw_domains: list[str], lst_path: Path) -> None:
    """Генерирует .lst (очищенный), .yaml и .mrs для одного исходного файла."""
    filtered_domains = clean_and_sort_domains(raw_domains)

    if not filtered_domains:
        print(f"[SKIP] Пустой список, пропускаем: {lst_path.relative_to(ROOT)}")
        return

    yaml_path = lst_path.with_suffix(".yaml")
    mrs_path  = lst_path.with_suffix(".mrs")

    # 1. Перезаписываем .lst — чистые уникальные домены, один на строку
    with lst_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(filtered_domains) + "\n")
    print(f"[OK]   .lst обновлён: {lst_path.relative_to(ROOT)}  ({len(filtered_domains)} доменов)")

    # 2. Генерируем .yaml в формате ClashX (Legacy rule-set)
    with yaml_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("payload:\n")
        for d in filtered_domains:
            f.write(f"  - '+.{d}'\n")
    print(f"[OK]   .yaml записан: {yaml_path.relative_to(ROOT)}")

    # 3. Компилируем бинарный .mrs через mihomo
    try:
        print(f"[...] Компиляция MRS: {mrs_path.name}")
        result = subprocess.run(
            ["mihomo", "convert-ruleset", "domain", "yaml", str(yaml_path), str(mrs_path)],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        if result.stdout:
            print(result.stdout.strip())
        print(f"[OK]   .mrs скомпилирован: {mrs_path.relative_to(ROOT)}")
    except FileNotFoundError:
        print("FATAL: исполняемый файл 'mihomo' не найден в PATH!", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"FATAL: ошибка компиляции MRS для {mrs_path.name}:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    print(f"ROOT репозитория: {ROOT}\n")

    lst_files = [
        p for p in ROOT.rglob("*.lst")
        if not any(part in SKIP_PARTS for part in p.parts)
    ]

    if not lst_files:
        print("Файлы .lst не найдены — нечего обрабатывать.", file=sys.stderr)
        return 1

    print(f"Найдено .lst файлов: {len(lst_files)}\n")

    errors = 0
    for lst_path in sorted(lst_files):
        try:
            raw_domains = lines_from_file(lst_path)
            generate_all_formats(raw_domains, lst_path)
        except Exception as e:
            print(f"[ERR]  {lst_path.relative_to(ROOT)}: {e}", file=sys.stderr)
            errors += 1
        print()

    if errors:
        print(f"\nЗавершено с ошибками: {errors} файл(ов) не обработано.", file=sys.stderr)
        return 1

    print("Все файлы успешно обработаны.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
