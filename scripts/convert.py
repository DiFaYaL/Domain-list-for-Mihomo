#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Папки, которые скрипт гарантированно игнорирует
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
            # Очищаем от спецсимволов переноса
            line = line.replace("\r", "").replace("\n", "")
            # Отрезаем комментарии
            if "#" in line:
                line = line.split("#", 1)[0]
            line = line.strip()
            if line:
                result.append(line)
    return result

def to_mrs(domains):
    out = []
    seen = set()

    for d in domains:
        value = d.strip()
        if not value:
            continue

        # Сохраняем домены "as is"
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
        print(f"Пропуск пустого файла: {lst_path}")
        return

    # Пути для файлов
    tmp_txt_path = lst_path.with_suffix(".tmp.txt")
    mrs_path = lst_path.with_suffix(".mrs")
    log_txt_path = lst_path.with_suffix(".txt")  # Наш файл-логгер

    # 1. Записываем чистые строки во временный файл для компилятора Mihomo
    with tmp_txt_path.open("w", encoding="utf-8") as f:
        for d in domains:
            f.write(f"{d}\n")

    # 2. Записываем полную структуру payload в постоянный .txt логгер для контроля глазами
    with log_txt_path.open("w", encoding="utf-8") as f:
        f.write("# Финальный лог компиляции для Mihomo Rule Set\n")
        f.write("payload:\n")
        for d in domains:
            f.write(f"  - '{d}'\n")

    try:
        # Компилируем .mrs
        subprocess.run(
            ["mihomo", "convert-ruleset", "domain", "text", str(tmp_txt_path), str(mrs_path)],
            check=True,
            cwd=ROOT,
        )
        print(f"Успешно скомпилировано и залогировано: {lst_path.name}")
    except FileNotFoundError:
        print("Ошибка: исполняемый файл mihomo не найден в системе!")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка компиляции для файла {lst_path.name}: {e}")
    finally:
        # Удаляем только временный файл, логгер остается
        tmp_txt_path.unlink(missing_ok=True)

def main():
    files = list(iter_lst_files())

    if not files:
        print("Файлы формата .lst не найдены")
        return 0

    for lst_path in files:
        domains = lines_from_file(lst_path)
        mrs_domains = to_mrs(domains)
        compile_mrs(mrs_domains, lst_path)

    return 0

if __name__ == "__main__":
    sys.exit(main())
