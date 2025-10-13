imghdr_fix"""
Файл для замены удаленного модуля imghdr в Python 3.11+
"""
import os

def what(file):
    """
    Определяет тип изображения по файлу
    Упрощенная версия для замены imghdr
    """
    if not os.path.isfile(file):
        return None

    try:
        with open(file, 'rb') as f:
            header = f.read(12)
    except IOError:
        return None

    # Проверка JPEG
    if header.startswith(b'\xff\xd8\xff'):
        return 'jpeg'

    # Проверка PNG
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'

    # Проверка GIF
    if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
        return 'gif'

    # Проверка BMP
    if header.startswith(b'BM'):
        return 'bmp'

    # Проверка WebP
    if header.startswith(b'RIFF') and header[8:12] == b'WEBP':
        return 'webp'

    return None