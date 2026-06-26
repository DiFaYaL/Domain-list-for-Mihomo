import os
import subprocess

def compile_lst_files():
    # Рекурсивно обходим весь репозиторий в поиске файлов .lst
    for root, dirs, files in os.walk("."):
        # Пропускаем служебные папки GitHub и виртуального окружения
        if ".git" in root or ".github" in root:
            continue
            
        for file_name in files:
            if file_name.endswith(".lst"):
                source_path = os.path.join(root, file_name)
                
                # Имя выходного бинарного файла .mrs (сохраняется в той же папке)
                base_name = os.path.splitext(file_name)[0]
                output_mrs_path = os.path.join(root, f"{base_name}.mrs")
                
                # Временный YAML-файл, в который мы запишем правильную структуру payload
                temp_yaml_path = os.path.join(root, f"temp_{base_name}.yaml")
                
                print(f"Обработка исходного файла правил: {source_path}")
                
                # Читаем домены, очищаем от пробелов и убираем комментарии
                with open(source_path, "r", encoding="utf-8") as f:
                    domains = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
                
                # Генерируем валидный YAML с обязательным заголовком payload
                with open(temp_yaml_path, "w", encoding="utf-8") as f:
                    f.write("payload:\n")
                    for domain in domains:
                        f.write(f"  - '{domain}'\n")
                
                # Запускаем компиляцию бинарного правила MRS через установленный в системе mihomo
                try:
                    print(f"Компиляция {file_name} -> {base_name}.mrs...")
                    subprocess.run(
                        ["mihomo", "convert-ruleset", "domain", "yaml", temp_yaml_path, output_mrs_path],
                        check=True
                    )
                    print(f"Успешно скомпилировано и сохранено в: {output_mrs_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Ошибка при сборке файла {file_name}: {e}")
                except FileNotFoundError:
                    print("Критическая ошибка: Ядро 'mihomo' не найдено в переменной PATH окружения!")
                finally:
                    # Удаляем временный файл конфигурации, чтобы не засорять репозиторий
                    if os.path.exists(temp_yaml_path):
                        os.remove(temp_yaml_path)

if __name__ == "__main__":
    compile_lst_files()
