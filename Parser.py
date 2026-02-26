import os
import sys
from pathlib import Path
from typing import Optional, Set
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Расширения файлов для полного чтения содержимого
READABLE_EXTENSIONS = {'.py', '.txt', '.md', '.json', '.yml', '.yaml', '.xml', '.html', '.css', '.js'}

# Расширения для игнорирования
IGNORED_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin', '.o', '.a'}

# Папки для игнорирования
IGNORED_DIRS = {'.git', '__pycache__', '.venv', 'venv', '.env', 'node_modules', '.idea', '.vscode'}

def get_ignored_dirs() -> Set[str]:
    """Возвращает набор папок, которые нужно игнорировать при обходе."""
    return IGNORED_DIRS.copy()

def should_skip_dir(dir_name: str, ignored_dirs: Set[str]) -> bool:
    """Проверяет, нужно ли пропустить директорию."""
    return dir_name in ignored_dirs

def get_file_size(file_path: str) -> str:
    """Получает размер файла в удобном формате."""
    try:
        size_bytes = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"
    except Exception as e:
        logger.warning(f"Не удалось получить размер файла {file_path}: {e}")
        return "N/A"

def read_file_safely(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """Безопасно читает содержимое файла."""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Пробуем альтернативные кодировки
        for alt_encoding in ['latin-1', 'cp1252', 'utf-16']:
            try:
                with open(file_path, 'r', encoding=alt_encoding) as f:
                    return f.read()
            except Exception:
                continue
        return None
    except Exception as e:
        logger.error(f"Ошибка чтения файла {file_path}: {e}")
        return None

def collect_files_info(source_dir: str, output_file: str, verbose: bool = False) -> bool:
    """
    Рекурсивно обходит source_dir и записывает информацию о файлах в output_file.
    
    Args:
        source_dir: Путь к исходной папке
        output_file: Путь к выходному файлу
        verbose: Показывать ли подробную информацию о каждом файле
    
    Returns:
        True если успешно, False если ошибка
    """
    try:
        ignored_dirs = get_ignored_dirs()
        file_count = 0
        
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(f"Анализ папки: {os.path.abspath(source_dir)}\n")
            out.write("=" * 80 + "\n\n")
            
            for root, dirs, files in os.walk(source_dir):
                # Фильтруем директории для пропуска
                dirs[:] = [d for d in dirs if not should_skip_dir(d, ignored_dirs)]
                
                for file in sorted(files):  # Сортируем файлы для наглядности
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, source_dir)
                    
                    # Проверяем расширение
                    _, ext = os.path.splitext(file)
                    
                    # Пропускаем бинарные файлы
                    if ext in IGNORED_EXTENSIONS:
                        if verbose:
                            out.write(f"[ПРОПУЩЕН] {rel_path} (бинарный файл)\n")
                        continue
                    
                    file_count += 1
                    file_size = get_file_size(file_path)
                    
                    out.write(f"### Файл: {rel_path} ({file_size}) ###\n")
                    out.write("-" * 80 + "\n")
                    
                    if ext in READABLE_EXTENSIONS or ext == '.py':
                        content = read_file_safely(file_path)
                        if content is not None:
                            out.write(content)
                            if not content.endswith('\n'):
                                out.write('\n')
                        else:
                            out.write(f"[ОШИБКА] Не удалось прочитать файл (кодировка не определена)\n")
                    else:
                        # Для остальных файлов выводим информацию
                        out.write(f"[ИНФОРМАЦИЯ] Файл типа: {ext.lstrip('.').upper() if ext else 'без расширения'}\n")
                    
                    out.write("\n" + "=" * 80 + "\n\n")
            
            out.write(f"\nВсего обработано файлов: {file_count}\n")
            logger.info(f"Обработано {file_count} файлов")
        
        return True
    
    except Exception as e:
        logger.error(f"Критическая ошибка при обработке папки: {e}")
        return False

def get_user_input(prompt: str, validate_func=None) -> Optional[str]:
    """Получает и валидирует пользовательский ввод."
    
    Args:
        prompt: Текст приглашения
        validate_func: Функция для валидации (возвращает True если валидно)
    
    Returns:
        Строка ввода пользователя или None если невалидно
    """
    while True:
        user_input = input(prompt).strip()
        
        if not user_input:
            print("❌ Ввод не может быть пустым.")
            continue
        
        if validate_func and not validate_func(user_input):
            continue
        
        return user_input

def validate_source_dir(path: str) -> bool:
    """Валидирует путь к исходной папке."""
    if not os.path.isdir(path):
        print(f"❌ Папка '{path}' не существует или это не папка.")
        return False
    return True

def validate_output_dir(path: str) -> bool:
    """Валидирует и создаёт папку для сохранения."""
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"✓ Папка '{path}' создана.")
        elif not os.path.isdir(path):
            print(f"❌ Путь '{path}' существует, но это не папка.")
            return False
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании папки: {e}")
        return False

def validate_filename(filename: str) -> bool:
    """Валидирует имя файла."""
    invalid_chars = '<>:"|?*'
    if any(char in filename for char in invalid_chars):
        print(f"❌ Имя файла содержит недопустимые символы: {invalid_chars}")
        return False
    return True

def main():
    """Главная функция программы."""
    print("\n" + "=" * 80)
    print("  Программа для анализа папки и сбора информации о файлах")
    print("=" * 80 + "\n")
    
    # Получаем путь к исходной папке
    source = get_user_input(
        "📁 Введите путь к исходной папке: ",
        validate_func=validate_source_dir
    )
    if not source:
        return
    
    # Получаем путь к папке для сохранения
    dest_dir = get_user_input(
        "📂 Введите путь к папке для сохранения результата: ",
        validate_func=validate_output_dir
    )
    if not dest_dir:
        return
    
    # Получаем имя выходного файла
    while True:
        filename = get_user_input(
            "📄 Введите имя итогового файла (например, result.txt): ",
            validate_func=validate_filename
        )
        if filename:
            if not filename.lower().endswith('.txt'):
                filename += '.txt'
            break
    
    output_file = os.path.join(dest_dir, filename)
    
    # Спрашиваем о подробном выводе
    verbose = input("\n🔍 Показывать информацию о пропущенных файлах? (y/n): ").strip().lower() == 'y'
    
    # Выполняем анализ
    print(f"\n⏳ Анализ папки '{source}'...\n")
    
    if collect_files_info(source, output_file, verbose):
        print(f"\n✅ Информация успешно сохранена в файл: {output_file}")
        print(f"📊 Размер файла: {get_file_size(output_file)}")
    else:
        print("\n❌ Произошла ошибка при обработке папки.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Программа прервана пользователем.")
        sys.exit(0)