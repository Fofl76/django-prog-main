# bookings/pdf_utils.py

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.rl_config import defaultPageSize
from django.http import HttpResponse
from django.utils import timezone
from .models import Room, Booking, Payment, Review, SpecialOffer

# Функция для безопасного отображения русского текста
def safe_text(text):
    """Преобразует текст для безопасного отображения в PDF"""
    if text is None:
        return ""
    # Убираем проблемные символы и заменяем на безопасные
    replacements = {
        'ё': 'е', 'Ё': 'Е',
        '—': '-', '–': '-',
        '"': '"', '"': '"',
        ''': "'", ''': "'",
        '…': '...',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return str(text)

def transliterate_text(text):
    """Транслитерирует русский текст в латинский для совместимости с PDF"""
    if text is None:
        return ""
    
    # Словарь транслитерации
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }
    
    result = ""
    for char in str(text):
        result += translit_dict.get(char, char)
    
    return result

def get_text_for_pdf(text, use_transliteration=False):
    """Возвращает текст, подготовленный для PDF"""
    if use_transliteration:
        return transliterate_text(text)
    else:
        return safe_text(text)

# Настройка шрифтов для поддержки кириллицы
def setup_fonts():
    """Настраивает шрифты для поддержки кириллицы"""
    try:
        # Попытка использовать встроенный Unicode шрифт
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        return 'STSong-Light'
    except:
        try:
            # Попытка использовать другой Unicode шрифт
            from reportlab.pdfbase.cidfonts import UnicodeCIDFont
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
            return 'HeiseiMin-W3'
        except:
            try:
                # Попытка зарегистрировать TTF шрифт
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                return 'DejaVuSans'
            except:
                try:
                    # Альтернативный шрифт
                    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                    return 'Arial'
                except:
                    # Если шрифты не найдены, используем стандартный
                    return 'Helvetica'

def setup_windows_fonts():
    """Настраивает шрифты Windows для поддержки кириллицы"""
    import os
    import platform
    
    if platform.system() == 'Windows':
        # Пути к шрифтам Windows
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
                    return font_name
                except:
                    continue
    
    # Если Windows шрифты не найдены, используем стандартную настройку
    return setup_fonts()

# Инициализируем шрифт
DEFAULT_FONT = setup_windows_fonts()


class PDFGenerator:
    def __init__(self, buffer=None):
        self.buffer = buffer or io.BytesIO()
        self.doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Создаем кастомные стили с поддержкой кириллицы
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            fontName=DEFAULT_FONT
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkgreen,
            fontName=DEFAULT_FONT
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.black,
            fontName=DEFAULT_FONT
        )
        
        # Обновляем стандартные стили для поддержки кириллицы
        self.styles['Normal'].fontName = DEFAULT_FONT
        self.styles['Heading1'].fontName = DEFAULT_FONT
        self.styles['Heading2'].fontName = DEFAULT_FONT
        self.styles['Heading3'].fontName = DEFAULT_FONT

    def add_title(self, title):
        """Добавляет заголовок документа"""
        safe_title = get_text_for_pdf(title)
        self.story.append(Paragraph(safe_title, self.title_style))
        self.story.append(Spacer(1, 20))

    def add_subtitle(self, subtitle):
        """Добавляет подзаголовок"""
        safe_subtitle = get_text_for_pdf(subtitle)
        self.story.append(Paragraph(safe_subtitle, self.subtitle_style))
        self.story.append(Spacer(1, 15))

    def add_header(self, header):
        """Добавляет заголовок раздела"""
        safe_header = get_text_for_pdf(header)
        self.story.append(Paragraph(safe_header, self.header_style))
        self.story.append(Spacer(1, 10))

    def add_table(self, data, headers=None):
        """Добавляет таблицу"""
        # Безопасно обрабатываем данные таблицы
        safe_data = []
        for row in data:
            safe_row = [get_text_for_pdf(str(cell)) for cell in row]
            safe_data.append(safe_row)
        
        if headers:
            safe_headers = [get_text_for_pdf(str(header)) for header in headers]
            table_data = [safe_headers] + safe_data
        else:
            table_data = safe_data
            
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), DEFAULT_FONT),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), DEFAULT_FONT),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def add_paragraph(self, text):
        """Добавляет параграф текста"""
        safe_text_content = get_text_for_pdf(text)
        self.story.append(Paragraph(safe_text_content, self.styles['Normal']))
        self.story.append(Spacer(1, 12))

    def add_page_break(self):
        """Добавляет разрыв страницы"""
        self.story.append(PageBreak())

    def build(self):
        """Строит PDF документ"""
        self.doc.build(self.story)
        return self.buffer

    def get_response(self, filename):
        """Возвращает HTTP ответ с PDF"""
        buffer = self.build()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


def generate_room_statistics_pdf_unicode():
    """Генерирует PDF с статистикой комнат используя Unicode шрифты"""
    generator = PDFGenerator()
    
    # Заголовок
    generator.add_title("Статистика комнат гостиницы")
    generator.add_paragraph(f"Отчет сгенерирован: {timezone.now().strftime('%d.%m.%Y %H:%M')}")
    generator.add_paragraph("=" * 50)
    
    # Получаем статистику комнат
    room_stats = Room.get_room_statistics()
    
    # Таблица статистики комнат
    generator.add_subtitle("Общая статистика комнат")
    
    headers = ['Номер', 'Тип', 'Цена/ночь', 'Средний рейтинг', 'Бронирования', 'Отмены', 'Доход', 'Средняя длительность']
    data = []
    
    for room in room_stats:
        avg_rating = room.avg_rating or 0
        cancellation_rate = room.cancellation_rate or 0
        total_revenue = room.total_revenue or 0
        avg_stay = room.avg_stay_duration or 0
        
        data.append([
            room.room_number,
            room.room_type,
            f"{room.price_per_night} ₽",
            f"{avg_rating:.1f}",
            str(room.total_bookings),
            f"{cancellation_rate:.1f}%",
            f"{total_revenue:.0f} ₽",
            f"{avg_stay.days if avg_stay else 0} дн."
        ])
    
    generator.add_table(data, headers)
    
    # Статистика по типам комнат
    generator.add_subtitle("Статистика по типам комнат")
    popular_types = Room.get_popular_room_types()
    
    headers = ['Тип комнаты', 'Количество', 'Бронирования', 'Средняя цена', 'Средний рейтинг', 'Общий доход']
    data = []
    
    for room_type in popular_types:
        avg_rating = room_type['avg_rating'] or 0
        total_revenue = room_type['total_revenue'] or 0
        
        data.append([
            room_type['room_type'],
            str(room_type['rooms_count']),
            str(room_type['bookings_count']),
            f"{room_type['avg_price']:.0f} ₽",
            f"{avg_rating:.1f}",
            f"{total_revenue:.0f} ₽"
        ])
    
    generator.add_table(data, headers)
    
    # Комнаты с активными предложениями
    generator.add_subtitle("Комнаты с активными специальными предложениями")
    rooms_with_offers = Room.get_rooms_with_special_offers()
    
    if rooms_with_offers.exists():
        headers = ['Номер', 'Тип', 'Обычная цена', 'Цена со скидкой', 'Макс. скидка']
        data = []
        
        for room in rooms_with_offers:
            current_price = room.get_current_price_with_discount()
            max_discount = room.get_max_discount_percentage()
            
            data.append([
                room.room_number,
                room.room_type,
                f"{room.price_per_night} ₽",
                f"{current_price:.0f} ₽",
                f"{max_discount:.1f}%"
            ])
        
        generator.add_table(data, headers)
    else:
        generator.add_paragraph("Нет комнат с активными специальными предложениями")
    
    return generator.get_response("room_statistics_unicode.pdf")


def generate_room_statistics_pdf_translit():
    """Генерирует PDF с статистикой комнат используя транслитерацию"""
    generator = PDFGenerator()
    
    # Заголовок
    generator.add_title("Statistika komnat gostinitsy")
    generator.add_paragraph(f"Otchet sgenerirovan: {timezone.now().strftime('%d.%m.%Y %H:%M')}")
    generator.add_paragraph("=" * 50)
    
    # Получаем статистику комнат
    room_stats = Room.get_room_statistics()
    
    # Таблица статистики комнат
    generator.add_subtitle("Obshchaya statistika komnat")
    
    headers = ['Nomer', 'Tip', 'Tsena/noch', 'Sredniy reyting', 'Bronirovaniya', 'Otmene', 'Dokhod', 'Srednyaya dlitelnost']
    data = []
    
    for room in room_stats:
        avg_rating = room.avg_rating or 0
        cancellation_rate = room.cancellation_rate or 0
        total_revenue = room.total_revenue or 0
        avg_stay = room.avg_stay_duration or 0
        
        data.append([
            room.room_number,
            transliterate_text(room.room_type),
            f"{room.price_per_night} R",
            f"{avg_rating:.1f}",
            str(room.total_bookings),
            f"{cancellation_rate:.1f}%",
            f"{total_revenue:.0f} R",
            f"{avg_stay.days if avg_stay else 0} dn."
        ])
    
    generator.add_table(data, headers)
    
    # Статистика по типам комнат
    generator.add_subtitle("Statistika po tipam komnat")
    popular_types = Room.get_popular_room_types()
    
    headers = ['Tip komnaty', 'Kolichestvo', 'Bronirovaniya', 'Srednyaya tsena', 'Sredniy reyting', 'Obshchiy dokhod']
    data = []
    
    for room_type in popular_types:
        avg_rating = room_type['avg_rating'] or 0
        total_revenue = room_type['total_revenue'] or 0
        
        data.append([
            transliterate_text(room_type['room_type']),
            str(room_type['rooms_count']),
            str(room_type['bookings_count']),
            f"{room_type['avg_price']:.0f} R",
            f"{avg_rating:.1f}",
            f"{total_revenue:.0f} R"
        ])
    
    generator.add_table(data, headers)
    
    # Комнаты с активными предложениями
    generator.add_subtitle("Komnaty s aktivnymi spetsialnymi predlozheniyami")
    rooms_with_offers = Room.get_rooms_with_special_offers()
    
    if rooms_with_offers.exists():
        headers = ['Nomer', 'Tip', 'Obychnaya tsena', 'Tsena so skidkoy', 'Maks. skidka']
        data = []
        
        for room in rooms_with_offers:
            current_price = room.get_current_price_with_discount()
            max_discount = room.get_max_discount_percentage()
            
            data.append([
                room.room_number,
                transliterate_text(room.room_type),
                f"{room.price_per_night} R",
                f"{current_price:.0f} R",
                f"{max_discount:.1f}%"
            ])
        
        generator.add_table(data, headers)
    else:
        generator.add_paragraph("Net komnat s aktivnymi spetsialnymi predlozheniyami")
    
    return generator.get_response("room_statistics_translit.pdf")


def generate_room_statistics_html_pdf():
    """Альтернативная версия с использованием HTML для лучшей поддержки кириллицы"""
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        from django.template.loader import get_template
        from django.template import Context
        
        # Получаем данные
        room_stats = Room.get_room_statistics()
        popular_types = Room.get_popular_room_types()
        rooms_with_offers = Room.get_rooms_with_special_offers()
        
        # Создаем HTML контент
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                h2 {{ color: #27ae60; border-bottom: 2px solid #3498db; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Статистика комнат гостиницы</h1>
                <p>Отчет сгенерирован: {timezone.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>Общая статистика комнат</h2>
                <table>
                    <tr>
                        <th>Номер</th>
                        <th>Тип</th>
                        <th>Цена/ночь</th>
                        <th>Средний рейтинг</th>
                        <th>Бронирования</th>
                        <th>Отмены</th>
                        <th>Доход</th>
                        <th>Средняя длительность</th>
                    </tr>
        """
        
        for room in room_stats:
            avg_rating = room.avg_rating or 0
            cancellation_rate = room.cancellation_rate or 0
            total_revenue = room.total_revenue or 0
            avg_stay = room.avg_stay_duration or 0
            
            html_content += f"""
                    <tr>
                        <td>{room.room_number}</td>
                        <td>{room.room_type}</td>
                        <td>{room.price_per_night} ₽</td>
                        <td>{avg_rating:.1f}</td>
                        <td>{room.total_bookings}</td>
                        <td>{cancellation_rate:.1f}%</td>
                        <td>{total_revenue:.0f} ₽</td>
                        <td>{avg_stay.days if avg_stay else 0} дн.</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Статистика по типам комнат</h2>
                <table>
                    <tr>
                        <th>Тип комнаты</th>
                        <th>Количество</th>
                        <th>Бронирования</th>
                        <th>Средняя цена</th>
                        <th>Средний рейтинг</th>
                        <th>Общий доход</th>
                    </tr>
        """
        
        for room_type in popular_types:
            avg_rating = room_type['avg_rating'] or 0
            total_revenue = room_type['total_revenue'] or 0
            
            html_content += f"""
                    <tr>
                        <td>{room_type['room_type']}</td>
                        <td>{room_type['rooms_count']}</td>
                        <td>{room_type['bookings_count']}</td>
                        <td>{room_type['avg_price']:.0f} ₽</td>
                        <td>{avg_rating:.1f}</td>
                        <td>{total_revenue:.0f} ₽</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        """
        
        if rooms_with_offers.exists():
            html_content += """
            <div class="section">
                <h2>Комнаты с активными специальными предложениями</h2>
                <table>
                    <tr>
                        <th>Номер</th>
                        <th>Тип</th>
                        <th>Обычная цена</th>
                        <th>Цена со скидкой</th>
                        <th>Макс. скидка</th>
                    </tr>
            """
            
            for room in rooms_with_offers:
                current_price = room.get_current_price_with_discount()
                max_discount = room.get_max_discount_percentage()
                
                html_content += f"""
                    <tr>
                        <td>{room.room_number}</td>
                        <td>{room.room_type}</td>
                        <td>{room.price_per_night} ₽</td>
                        <td>{current_price:.0f} ₽</td>
                        <td>{max_discount:.1f}%</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </div>
            """
        else:
            html_content += """
            <div class="section">
                <h2>Комнаты с активными специальными предложениями</h2>
                <p>Нет комнат с активными специальными предложениями</p>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        # Конвертируем HTML в PDF
        result = BytesIO()
        pdf = pisa.CreatePDF(BytesIO(html_content.encode("UTF-8")), result)
        
        if not pdf.err:
            result.seek(0)
            response = HttpResponse(result, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="room_statistics_html.pdf"'
            return response
        else:
            # Если HTML версия не сработала, используем ReportLab
            return generate_room_statistics_pdf_unicode()
            
    except ImportError:
        # Если xhtml2pdf не установлен, используем ReportLab
        return generate_room_statistics_pdf_unicode()


def generate_monthly_report_pdf(year, month):
    """Генерирует месячный отчет"""
    generator = PDFGenerator()
    
    month_names = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',
        7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    
    # Заголовок
    generator.add_title(f"Месячный отчет за {month_names[month]} {year}")
    generator.add_paragraph(f"Отчет сгенерирован: {timezone.now().strftime('%d.%m.%Y %H:%M')}")
    generator.add_paragraph("=" * 50)
    
    # Получаем месячную статистику
    monthly_stats = Room.get_monthly_statistics(year, month)
    
    # Таблица месячной статистики
    generator.add_subtitle(f"Статистика за {month_names[month]} {year}")
    
    headers = ['Номер', 'Бронирования', 'Доход', 'Занятые дни', 'Загрузка', 'Рейтинг', 'Отзывы']
    data = []
    
    for room in monthly_stats:
        occupancy_rate = room.occupancy_rate or 0
        monthly_rating = room.monthly_rating or 0
        
        data.append([
            room.room_number,
            str(room.monthly_bookings),
            f"{room.monthly_revenue:.0f} ₽",
            str(room.occupied_days),
            f"{occupancy_rate:.1f}%",
            f"{monthly_rating:.1f}",
            str(room.reviews_count)
        ])
    
    generator.add_table(data, headers)
    
    # Общая статистика за месяц
    generator.add_subtitle("Общая статистика за месяц")
    
    total_bookings = sum(room.monthly_bookings for room in monthly_stats)
    total_revenue = sum(room.monthly_revenue or 0 for room in monthly_stats)
    total_reviews = sum(room.reviews_count for room in monthly_stats)
    avg_rating = sum(room.monthly_rating or 0 for room in monthly_stats) / len(monthly_stats) if monthly_stats else 0
    
    summary_data = [
        ['Показатель', 'Значение'],
        ['Общее количество бронирований', str(total_bookings)],
        ['Общий доход', f"{total_revenue:.0f} ₽"],
        ['Количество отзывов', str(total_reviews)],
        ['Средний рейтинг', f"{avg_rating:.1f}"],
    ]
    
    generator.add_table(summary_data)
    
    return generator.get_response(f"monthly_report_{year}_{month:02d}.pdf")


def generate_booking_report_pdf():
    """Генерирует отчет по бронированиям"""
    generator = PDFGenerator()
    
    # Заголовок
    generator.add_title("Отчет по бронированиям")
    generator.add_paragraph(f"Отчет сгенерирован: {timezone.now().strftime('%d.%m.%Y %H:%M')}")
    generator.add_paragraph("=" * 50)
    
    # Статистика по статусам бронирований
    generator.add_subtitle("Статистика по статусам бронирований")
    
    from django.db.models import Count
    status_stats = Booking.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    headers = ['Статус', 'Количество']
    data = [[item['status'], str(item['count'])] for item in status_stats]
    generator.add_table(data, headers)
    
    # Последние бронирования
    generator.add_subtitle("Последние бронирования")
    
    recent_bookings = Booking.objects.select_related('guest', 'room').order_by('-created_at')[:20]
    
    headers = ['Гость', 'Комната', 'Заезд', 'Выезд', 'Статус', 'Сумма']
    data = []
    
    for booking in recent_bookings:
        data.append([
            booking.guest.username,
            booking.room.room_number,
            booking.check_in.strftime('%d.%m.%Y'),
            booking.check_out.strftime('%d.%m.%Y'),
            booking.get_status_display(),
            f"{booking.total_price():.0f} ₽"
        ])
    
    generator.add_table(data, headers)
    
    return generator.get_response("booking_report.pdf")


def generate_special_offers_report_pdf():
    """Генерирует отчет по специальным предложениям"""
    generator = PDFGenerator()
    
    # Заголовок
    generator.add_title("Отчет по специальным предложениям")
    generator.add_paragraph(f"Отчет сгенерирован: {timezone.now().strftime('%d.%m.%Y %H:%M')}")
    generator.add_paragraph("=" * 50)
    
    # Популярные предложения
    generator.add_subtitle("Популярные предложения")
    
    popular_offers = SpecialOffer.get_popular_offers()
    
    headers = ['Название', 'Количество применений', 'Активно']
    data = []
    
    for offer in popular_offers:
        active_count = offer.get_active_applications_count()
        data.append([
            offer.title,
            str(offer.applications_count),
            str(active_count)
        ])
    
    generator.add_table(data, headers)
    
    # Предложения с комнатами
    generator.add_subtitle("Предложения с примененными комнатами")
    
    offers_with_rooms = SpecialOffer.get_offers_with_rooms()
    
    for offer in offers_with_rooms:
        generator.add_header(f"Предложение: {offer.title}")
        
        active_rooms = offer.get_active_rooms()
        if active_rooms.exists():
            headers = ['Номер', 'Тип', 'Обычная цена', 'Цена со скидкой']
            data = []
            
            for room in active_rooms:
                room_offer = room.room_special_offers.filter(special_offer=offer).first()
                if room_offer:
                    discounted_price = room_offer.get_discounted_price()
                    data.append([
                        room.room_number,
                        room.room_type,
                        f"{room.price_per_night} ₽",
                        f"{discounted_price:.0f} ₽"
                    ])
            
            generator.add_table(data, headers)
        else:
            generator.add_paragraph("Нет активных применений")
        
        generator.add_paragraph("")
    
    return generator.get_response("special_offers_report.pdf") 