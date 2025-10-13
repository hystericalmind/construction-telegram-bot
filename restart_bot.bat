@echo off
echo 🔴 Завершаем все Python процессы...
taskkill /f /im python.exe /t
timeout /t 2 /nobreak
echo 🚀 Запускаем бота...
python main.py
pause