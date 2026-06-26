#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Папки, которые скрипт гарантированно будет пропускать при поиске списков
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
            # Очищаем строку от спецсимволов переноса строки
            line = line.replace("\r", "").replace("\n", "")
            # Отрезаем комментарии, если строка начинается с # или содержит комментарий в конце
            line = line.split("#", 1)[0].strip()
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

        # Сохраняем домен в исходном виде "as is" без принудительных префиксов +.
        if value not in seen:
            seen.add(value)
            out.append(value)

    return sorted(out)

def iter_lst_files():
    # Рекурсивно ищем все файлы .lst во всех папках репозитория
    for path in ROOT.rglob("*.lst"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path

def compile_mrs(domains, lst_path: Path):
    if not domains:
        print(f"Пропуск пустого файла: {lst_path}")
        return

    # Создаем временный текстовый файл и финальный .mrs рядом с исходным .lst
    txt_path = lst_path.with_suffix(".tmp.txt")
    mrs_path = lst_path.with_suffix(".mrs")

    with txt_path.open("w", encoding="utf-8") as f:
        for d in domains:
            f.write(f"{d}\n")

    try:
        # Компилируем через глобальную команду mihomo
        subprocess.run(
            ["mihomo", "convert-ruleset", "domain", "text", str(txt_path), str(mrs_path)],
            check=True,
            cwd=ROOT,
        )
        print(f"Успешно скомпилирован: {mrs_path.relative_to(ROOT)}")
    except FileNotFoundError:
        print("Критическая ошибка: Исполняемый файл 'mihomo' не найден в PATH системы!")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка компиляции для файла {lst_path.name}: {e}")
    finally:
        # Вычищаем за собой временный txt файл
        txt_path.unlink(missing_ok=True)

def main():
    files = list(iter_lst_files())

    if not files:
        print("Файлы формата .lst не найдены в репозитории.")
        return 0

    for lst_path in files:
        domains = lines_from_file(lst_path)
        mrs_domains = to_mrs(domains)
        compile_mrs(mrs_domains, lst_path)

    return 0

if __name__ == "__main__":
    sys.exit(main())
