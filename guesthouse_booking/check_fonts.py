#!/usr/bin/env python
"""
Скрипт для проверки доступных шрифтов и их поддержки кириллицы
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guesthouse_booking.settings')
django.setup()

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import platform

def check_fonts():
    """Проверяет доступные шрифты"""
    print("🔍 Проверка доступных шрифтов для PDF...")
    print(f"ОС: {platform.system()}")
    print()
    
    # Проверяем встроенные Unicode шрифты
    print("1. Встроенные Unicode шрифты ReportLab:")
    unicode_fonts = ['STSong-Light', 'HeiseiMin-W3', 'HeiseiKakuGo-W5']
    
    for font_name in unicode_fonts:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont(font_name))
            print(f"   ✅ {font_name} - доступен")
        except Exception as e:
            print(f"   ❌ {font_name} - недоступен: {str(e)}")
    
    print()
    
    # Проверяем системные шрифты Windows
    if platform.system() == 'Windows':
        print("2. Системные шрифты Windows:")
        font_paths = [
            r'C:\Windows\Fonts\arial.ttf',
            r'C:\Windows\Fonts\calibri.ttf',
            r'C:\Windows\Fonts\segoeui.ttf',
            r'C:\Windows\Fonts\tahoma.ttf',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font_name = os.path.splitext(os.path.basename(font_path))[0]
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"   ✅ {font_name} - доступен ({font_path})")
                except Exception as e:
                    print(f"   ❌ {font_name} - ошибка регистрации: {str(e)}")
            else:
                print(f"   ❌ {font_path} - файл не найден")
    
    print()
    
    # Проверяем другие шрифты
    print("3. Другие шрифты:")
    other_fonts = [
        ('DejaVuSans', 'DejaVuSans.ttf'),
        ('Arial', 'arial.ttf'),
    ]
    
    for font_name, font_file in other_fonts:
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_file))
            print(f"   ✅ {font_name} - доступен")
        except Exception as e:
            print(f"   ❌ {font_name} - недоступен: {str(e)}")
    
    print()
    print("💡 Рекомендации:")
    print("   - Если доступны Unicode шрифты, используйте их для лучшей поддержки кириллицы")
    print("   - Если доступны системные шрифты Windows, они также хорошо поддерживают кириллицу")
    print("   - В крайнем случае используйте транслитерацию")

if __name__ == "__main__":
    check_fonts() 