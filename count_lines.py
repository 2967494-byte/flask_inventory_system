import os

def count_python_lines(directory):
    total_lines = 0
    file_count = 0
    
    for root, dirs, files in os.walk(directory):
        # Пропускаем виртуальное окружение
        dirs[:] = [d for d in dirs if 'venv' not in d]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1
                        print(f"{filepath}: {lines} строк")
                except:
                    continue
    
    print(f"\n{'='*50}")
    print(f"📊 ИТОГО:")
    print(f"Файлов Python: {file_count}")
    print(f"Всего строк: {total_lines}")
    if file_count > 0:
        print(f"Среднее: {total_lines/file_count:.1f} строк на файл")

if __name__ == "__main__":
    count_python_lines(".")