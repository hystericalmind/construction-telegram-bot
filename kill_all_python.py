import os
import sys
import subprocess
import time


def kill_all_python():
    """Принудительно завершает все процессы Python"""
    print("🔴 Завершаем все Python процессы...")

    try:
        if sys.platform == "win32":
            # Для Windows
            result = subprocess.run(['taskkill', '/f', '/im', 'python.exe', '/t'],
                                    capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        else:
            # Для Linux/Mac
            os.system('pkill -9 -f python')

        print("✅ Все Python процессы завершены")
        time.sleep(2)  # Ждем завершения

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    kill_all_python()