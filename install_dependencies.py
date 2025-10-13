"""
Скрипт для установки зависимостей на PythonAnywhere
"""
import subprocess
import sys


def install_packages():
    packages = [
        "python-telegram-bot==20.7",
        "google-api-python-client==2.108.0",
        "google-auth-oauthlib==1.1.0",
        "gspread==5.12.0",
        "python-dotenv==1.0.0"
    ]

    for package in packages:
        print(f"Устанавливаю {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    print("✅ Все зависимости установлены!")


if __name__ == "__main__":
    install_packages()