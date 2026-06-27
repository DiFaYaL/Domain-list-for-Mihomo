#!/usr/bin/env python3
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {".git", ".github", "__pycache__", "scripts"}

def clean_and_sort_domains(domains: set[str]) -> list[str]:
    """Просто очищает строки и убирает точные дубликаты БЕЗ удаления поддоменов"""
    clean_set = set()
    for d in domains:
        d = d.strip()
        # Очищаем от случайных префиксов, если они были в исходнике
        if d.startswith("+."): d = d[2:]
        elif d.startswith("."): d = d[1:]
        if d:
            clean_set.add(d)
    # Возвращаем просто отсортированный по алфавиту список
    return sorted(list(clean_set))

def lines_from_file(filepath: Path):
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

def generate_all_formats(raw_domains, lst_path: Path):
    # Теперь здесь простая очистка без вредного алгоритма сокращения
    filtered_domains = clean_and_sort_domains(raw_domains)
    if not filtered_domains:
        print(f"Пропуск пустого файла: {lst_path.name}")
        return

    yaml_path = lst_path.with_suffix(".yaml")
    final_lst_path = lst_path

    # 1. Перезаписываем .lst файл чистыми строками БЕЗ удаления ваших поддоменов
    with final_lst_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(filtered_domains) + "\n")

    # 2. Генерируем .yaml файл строго по стандарту (с 4 пробелами и префиксом +.)
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
