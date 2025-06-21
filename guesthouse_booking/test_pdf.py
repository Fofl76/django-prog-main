#!/usr/bin/env python
"""
Тестовый скрипт для проверки генерации PDF с русским текстом
"""

import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guesthouse_booking.settings')
django.setup()

from bookings.pdf_utils import (
    generate_room_statistics_html_pdf, 
    generate_room_statistics_pdf_unicode,
    generate_room_statistics_pdf_translit
)

def test_pdf_generation():
    """Тестирует генерацию PDF с русским текстом"""
    print("Тестирование генерации PDF...")
    
    try:
        # Тестируем Unicode версию
        print("1. Тестируем Unicode версию (встроенные шрифты ReportLab)...")
        response = generate_room_statistics_pdf_unicode()
        print(f"✅ Unicode версия успешно сгенерирована: {response['Content-Disposition']}")
        
        # Тестируем HTML версию
        print("2. Тестируем HTML версию (xhtml2pdf)...")
        response = generate_room_statistics_html_pdf()
        print(f"✅ HTML версия успешно сгенерирована: {response['Content-Disposition']}")
        
        # Тестируем транслитерированную версию
        print("3. Тестируем транслитерированную версию (латинские символы)...")
        response = generate_room_statistics_pdf_translit()
        print(f"✅ Транслитерированная версия успешно сгенерирована: {response['Content-Disposition']}")
        
        print("\n🎉 Все тесты прошли успешно!")
        print("📄 PDF файлы должны корректно отображать текст")
        print("💡 Unicode версия использует встроенные шрифты ReportLab")
        print("💡 HTML версия использует xhtml2pdf для лучшей поддержки кириллицы")
        print("💡 Транслитерированная версия использует латинские символы")
        
    except Exception as e:
        print(f"❌ Ошибка при генерации PDF: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_pdf_generation() 