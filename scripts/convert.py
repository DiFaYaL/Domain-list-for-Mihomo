#!/usr/bin/env python3
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {".git", ".github", "__pycache__", "scripts"}

def remove_overlaps(domains: set[str]) -> list[str]:
    """Умный алгоритм фильтрации поддоменов из оригинального репозитория"""
    clean_set = set()
    for d in domains:
        d = d.strip()
        if d.startswith("+."): d = d[2:]
        elif d.startswith("."): d = d[1:]
        if d: clean_set.add(d)

    sorted_domains = sorted(clean_set, key=lambda d: d.count("."))
    result = set()

    for domain in sorted_domains:
        parts = domain.split(".")
        skip = False
        for i in range(1, len(parts)):
            parent = ".".join(parts[i:])
            if parent in result:
                skip = True
                break
        if not skip:
            result.add(domain)

    return sorted(result)

def lines_from_file(filepath: Path):
    if not filepath.exists():
        return []
    result = []
    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.replace("\r", "").replace("\n", "")
            # Правильно отрезаем комментарии, оставляя только строку до знака #
            if "#" in line:
                line = line.split("#", 1)[0]
            line = line.strip()
            if line:
                result.append(line)
    return result

def generate_all_formats(raw_domains, lst_path: Path):
    # Применяем умную фильтрацию поддоменов
    filtered_domains = remove_overlaps(raw_domains)
    if not filtered_domains:
        print(f"Пропуск пустого файла: {lst_path.name}")
        return

    # Пути для трех типов файлов в той же папке
    yaml_path = lst_path.with_suffix(".yaml")
    final_lst_path = lst_path  # Перезаписываем исходный .lst, делая его чистым

    # 1. Перезаписываем .lst файл, делая его идеально чистым (как у них)
    with final_lst_path.open("w", encoding="utf-8", newline="\n") as f:
        # В .lst файлы записываются чистые домены без префиксов
        f.write("\n".join(filtered_domains) + "\n")

    # 2. Генерируем .yaml файл строго по их стандарту (с 4 пробелами и префиксом +.)
    with yaml_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("payload:\n")
        for d in filtered_domains:
            f.write(f"    - +.{d}\n")
    
    print(f"Успешно сгенерированы .lst и .yaml для: {lst_path.name} (Доменов: {len(filtered_domains)})")

def main():
    found = False
    for path in ROOT.rglob("*.lst"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        found = True
        raw_domains = lines_from_file(path)
        generate_all_formats(raw_domains, path)
    
    if not found:
        print("Файлы исходных списков .lst не найдены")
    return 0

if __name__ == "__main__":
    sys.exit(main())
