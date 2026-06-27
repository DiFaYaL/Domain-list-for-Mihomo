#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {".git", ".github", "__pycache__", "scripts"}

def clean_and_sort_domains(domains: set[str]) -> list[str]:
    """Очищает строки от пробелов, случайных префиксов и дубликатов"""
    clean_set = set()
    for d in domains:
        d = d.strip()
        # Очищаем от возможных префиксов, если они случайно закрались в исходник
        if d.startswith("DOMAIN-SUFFIX,"): d = d[len("DOMAIN-SUFFIX,"):]
        if d.startswith("+."): d = d[2:]
        elif d.startswith("."): d = d[1:]
        if d:
            clean_set.add(d)
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
    filtered_domains = clean_and_sort_domains(raw_domains)
    if not filtered_domains:
        print(f"Пропуск пустого файла: {lst_path.name}")
        return

    yaml_path = lst_path.with_suffix(".yaml")
    mrs_path = lst_path.with_suffix(".mrs")

    # 1. Перезаписываем исходный .lst файл идеально чистыми уникальными доменами
    with lst_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(filtered_domains) + "\n")

    # 2. Генерируем .yaml файл СТРОГО в синтаксисе ClashX (как inside-clashx.lst)
    with yaml_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("payload:\n")
        for d in filtered_domains:
            f.write(f"  - DOMAIN-SUFFIX,{d}\n")
    
    # 3. ПРОЦЕДУРА ГЕНЕРАЦИИ БИНАРНОГО .MRS ФАЙЛА (Вызов ядра из Python)
    try:
        print(f"Компиляция бинарника MRS для: {mrs_path.name}")
        subprocess.run(
            ["mihomo", "convert-ruleset", "domain", "yaml", str(yaml_path), str(mrs_path)],
            check=True,
            cwd=ROOT,
        )
        print(f"Успешно скомпилирован: {mrs_path.name}")
    except FileNotFoundError:
        print("Ошибка: исполняемый файл 'mihomo' не найден в переменной PATH системы!")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Критическая ошибка компиляции Mihomo для {mrs_path.name}: {e}")
        sys.exit(1)

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
