import sys
import subprocess
from pathlib import Path


# Корень проекта: папка, в которой лежит сама папка core/
# __file__ — это путь к текущему файлу tools.py
# resolve() превращает его в абсолютный путь
# parent — это папка core
# parent.parent — это корень проекта AI QA & Review Agent
BASE_DIR = Path(__file__).resolve().parent.parent

def run_tests(test_target: str) -> dict:
    """
    Запускает pytest для указанного файла или папки.
    Возвращает статус прохождения теста и текст вывода терминала.
    """
    # запуск команды pytest через системный процесс
    try:
        process = subprocess.run(
            [sys.executable, "-m", "pytest", test_target, "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )
        # код возврата 0 - тесты прошли, любое другое число - не прошли
        is_passed = process.returncode == 0
        output_text = process.stdout + process.stderr

        return {
            "passed": is_passed,
            "exit_code": process.returncode,
            "output": output_text,
        }
    except Exception as exc:
        return {
            "passed": False,
            "exit_code": -1,
            "output": f"Системная ошибка запуска тестов: {str(exc)}",
        }

def read_code_file(relative_path: str) -> dict:
    """
    Читает содержимое файла.
    Возвращает словарь с содержимым или описанием ошибки.
    """
    # Соединяем корень проекта с переданным путем через слэш
    target_path = (BASE_DIR / relative_path).resolve()

    # Защита: проверяем, что файл не пытается вылезти наружу проекта
    if not str(target_path).startswith(str(BASE_DIR)):
        return {"error": f"Доступ запрещен: путь выходит за пределы проекта -> {relative_path}"}

    # Проверяем, существует ли файл физически на диске
    if not target_path.exists():
        return {"error": f"Файл не найден: {relative_path}"}

    # Проверяем, что это именно файл, а не папка
    if not target_path.is_file():
        return {"error": f"Указанный путь является папкой, а не файлом: {relative_path}"}

    try:
        # Читаем весь текст файла в кодировке UTF-8
        code = target_path.read_text(encoding="utf-8")
        return {"content": code, "error": None}
    except Exception as exc:
        return {"error": f"Ошибка при чтении файла: {str(exc)}"}

def write_code_file(relative_path: str, content: str) -> dict:
    """
    Безопасно записывает сгенерированный код или тесты в файл внутри проекта.
    Автоматически создает недостающие папки, если их еще нет.
    """
    target_path = (BASE_DIR / relative_path).resolve()

    if not str(target_path).startswith(str(BASE_DIR)):
        return {
            "success": False,
            "error": f"Доступ запрещен: путь находится за пределами проекта -> {relative_path}",
        }
    try:
        # Создаем всю цепочку папок до файла, если их еще нет на диске
        target_path.parent.mkdir(parents=True, exist_ok=True)
        # Записываем текст в кодировке UTF-8 (создаст файл или перезапишет существующий)
        target_path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "error": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Ошибка при записи файла: {str(exc)}",
        }

if __name__ == "__main__":
    print("Проверяем работу инструмента:")
    # Попробуем запустить несуществующий файл, чтобы увидеть, как среагирует функция
    res = run_tests("non_existent_test.py")
    print(f"Тесты прошли успешно? -> {res['passed']}")
    print(f"Код завершения: {res['exit_code']}")
    print("Вывод терминала:")
    print(res["output"])
    print("--- Проверка инструмента чтения файлов ---")

    # 1. Пробуем прочитать сам этот файл tools.py
    self_read = read_code_file("core/tools.py")
    if self_read["error"]:
        print(f"Ошибка: {self_read['error']}")
    else:
        print(f"Файл успешно прочитан! Количество символов: {len(self_read['content'])}")
        print("Первые 100 символов:")
        print(self_read["content"][:100])

    # 2. Пробуем прочитать несуществующий файл
    bad_read = read_code_file("core/ghost.py")
    print(f"\nТест с несуществующим файлом: {bad_read}")

    print("1. Тест записи:", write_code_file("sandbox/hello_test.py", "def test_ok():\n    assert 1 == 1\n"))
    print("2. Тест защиты:", write_code_file("../hack.py", "print('boom')"))
