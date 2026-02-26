import os

def collect_files_info(source_dir, output_file):
    """
    Рекурсивно обходит source_dir и записывает информацию о файлах в output_file.
    """
    with open(output_file, 'w', encoding='utf-8') as out:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Относительный путь от исходной папки для наглядности
                rel_path = os.path.relpath(file_path, source_dir)
                out.write(f"### Путь: {rel_path} ###\n")

                if file.endswith('.py'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        out.write(content)
                        # Добавляем перевод строки, если его нет в конце файла
                        if not content.endswith('\n'):
                            out.write('\n')
                    except Exception as e:
                        out.write(f"Ошибка чтения .py файла: {e}\n")
                else:
                    # Для не-.py файлов выводим имя и расширение
                    name, ext = os.path.splitext(file)
                    ext = ext.lstrip('.').upper() if ext else 'нет расширения'
                    out.write(f"Это файл: {file} (формат: {ext})\n")
                out.write('\n')  # разделитель между файлами

def main():
    print("Программа для анализа папки и сбора информации о файлах.")
    source = input("Введите путь к исходной папке: ").strip()
    if not os.path.isdir(source):
        print("Указанная папка не существует или это не папка.")
        return

    dest_dir = input("Введите путь к папке для сохранения результата: ").strip()
    # Если папка назначения не существует — пробуем создать
    if not os.path.exists(dest_dir):
        try:
            os.makedirs(dest_dir)
        except Exception as e:
            print(f"Не удалось создать папку назначения: {e}")
            return
    elif not os.path.isdir(dest_dir):
        print("Указанный путь для сохранения не является папкой.")
        return

    filename = input("Введите имя итогового файла (например, result.txt): ").strip()
    if not filename:
        print("Имя файла не может быть пустым.")
        return
    # Добавляем расширение .txt, если его нет
    if not filename.lower().endswith('.txt'):
        filename += '.txt'

    output_file = os.path.join(dest_dir, filename)

    try:
        collect_files_info(source, output_file)
        print(f"Информация успешно сохранена в файл: {output_file}")
    except Exception as e:
        print(f"Произошла ошибка при обработке: {e}")

if __name__ == "__main__":
    main()