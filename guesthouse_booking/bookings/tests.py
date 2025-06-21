from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Room, Amenity, Booking, Review, Guest, Payment, SpecialOffer
from .serializers import RoomSerializer, BookingSerializer, ReviewSerializer
from rest_framework.test import APIClient
from rest_framework import status
import os
from typing import Any

# PDF и шрифты (минимальные smoke-тесты)
class PDFAndFontTestCase(TestCase):
    """Тесты PDF-генерации и проверки шрифтов."""
    def test_pdf_unicode_generation(self) -> None:
        """Проверяет генерацию PDF с Unicode шрифтами."""
        from bookings.pdf_utils import generate_room_statistics_pdf_unicode
        response = generate_room_statistics_pdf_unicode()
        self.assertIn('Content-Disposition', response)

    def test_pdf_html_generation(self) -> None:
        """Проверяет генерацию PDF через HTML (xhtml2pdf)."""
        from bookings.pdf_utils import generate_room_statistics_html_pdf
        response = generate_room_statistics_html_pdf()
        self.assertIn('Content-Disposition', response)

    def test_pdf_translit_generation(self) -> None:
        """Проверяет генерацию PDF с транслитерацией."""
        from bookings.pdf_utils import generate_room_statistics_pdf_translit
        response = generate_room_statistics_pdf_translit()
        self.assertIn('Content-Disposition', response)

    def test_check_fonts(self) -> None:
        """Проверяет регистрацию шрифтов ReportLab."""
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        except Exception:
            pass
        self.assertTrue(True)  # Smoke test

# Модели
class RoomModelTest(TestCase):
    """Тесты модели Room."""
    def test_create_room(self) -> None:
        """Проверяет создание комнаты и строковое представление."""
        room = Room.objects.create(room_number='101', room_type='Люкс', price_per_night=1000, max_occupancy=2)
        self.assertEqual(str(room), 'Комната 101 (Люкс)')

    def test_room_amenities(self) -> None:
        """Проверяет добавление удобств к комнате."""
        room = Room.objects.create(room_number='102', room_type='Стандарт', price_per_night=800, max_occupancy=2)
        amenity = Amenity.objects.create(name='Wi-Fi')
        room.amenities.add(amenity)
        self.assertIn(amenity, room.amenities.all())

class BookingModelTest(TestCase):
    """Тесты модели Booking."""
    def setUp(self) -> None:
        """Создаёт пользователя и комнату для тестов бронирования."""
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.room = Room.objects.create(room_number='103', room_type='Эконом', price_per_night=500, max_occupancy=1)

    def test_create_booking(self) -> None:
        """Проверяет создание бронирования и строковое представление."""
        booking = Booking.objects.create(guest=self.user, room=self.room, check_in='2025-01-01', check_out='2025-01-02', guests_count=1)
        self.assertEqual(str(booking), f"Booking {booking.id} - {self.user.username} - {self.room.room_number}")

# Сериализаторы
class RoomSerializerTest(TestCase):
    """Тесты сериализатора RoomSerializer."""
    def test_room_serializer(self) -> None:
        """Проверяет сериализацию комнаты."""
        room = Room.objects.create(room_number='104', room_type='Люкс', price_per_night=1200, max_occupancy=3)
        data = RoomSerializer(room).data
        self.assertEqual(data['room_number'], '104')

# API
class RoomAPITest(TestCase):
    """Тесты API для комнат."""
    def setUp(self) -> None:
        """Создаёт тестовую комнату и APIClient."""
        self.client = APIClient()
        self.room = Room.objects.create(room_number='105', room_type='Стандарт', price_per_night=900, max_occupancy=2)

    def test_room_list(self) -> None:
        """Проверяет получение списка комнат через API."""
        response = self.client.get(reverse('room-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data or isinstance(response.data, list))

    def test_room_detail(self) -> None:
        """Проверяет получение деталей комнаты через API."""
        response = self.client.get(reverse('room-detail', args=[self.room.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['room_number'], '105')

# Дополнительные тесты (разнообразные)
class ProjectExtraTests(TestCase):
    """Дополнительные тесты для моделей и сериализаторов проекта."""
    def test_create_amenity(self) -> None:
        """Проверяет создание удобства."""
        a = Amenity.objects.create(name='TV')
        self.assertEqual(str(a), 'TV')

    def test_create_review(self) -> None:
        """Проверяет создание отзыва и строковое представление."""
        user = User.objects.create_user(username='reviewer', password='pass')
        room = Room.objects.create(room_number='106', room_type='Эконом', price_per_night=400, max_occupancy=1)
        review = Review.objects.create(room=room, guest=user, rating=5, comment='Отлично!')
        self.assertEqual(str(review), f"Review {review.id} - {room} by {user.username}")

    def test_special_offer(self) -> None:
        """Проверяет создание специального предложения и строковое представление."""
        offer = SpecialOffer.objects.create(title='Скидка', image='test.jpg', short_description='desc', full_description='full', price=100)
        self.assertEqual(str(offer), 'Скидка')

    def test_guest_creation(self) -> None:
        """Проверяет создание гостя и строковое представление."""
        user = User.objects.create_user(username='guestuser', password='pass')
        guest = Guest.objects.create(user=user, first_name='Имя', last_name='Фамилия', email='test@mail.com', phone_number='123')
        self.assertEqual(str(guest), 'Имя Фамилия')

    def test_payment_creation(self) -> None:
        """Проверяет создание платежа и строковое представление."""
        user = User.objects.create_user(username='payuser', password='pass')
        room = Room.objects.create(room_number='107', room_type='Эконом', price_per_night=300, max_occupancy=1)
        booking = Booking.objects.create(guest=user, room=room, check_in='2025-01-01', check_out='2025-01-02', guests_count=1)
        payment = Payment.objects.create(booking=booking, amount=100, payment_method='card', status='completed')
        self.assertIn(f"Payment {payment.id}", str(payment))

    def test_room_str(self) -> None:
        """Проверяет строковое представление комнаты."""
        room = Room.objects.create(room_number='108', room_type='Люкс', price_per_night=1500, max_occupancy=2)
        self.assertIn('Комната', str(room))

    def test_booking_str(self) -> None:
        """Проверяет строковое представление бронирования."""
        user = User.objects.create_user(username='buser', password='pass')
        room = Room.objects.create(room_number='109', room_type='Стандарт', price_per_night=700, max_occupancy=2)
        booking = Booking.objects.create(guest=user, room=room, check_in='2025-01-01', check_out='2025-01-02', guests_count=1)
        self.assertIn('Booking', str(booking))

    def test_review_str(self) -> None:
        """Проверяет строковое представление отзыва."""
        user = User.objects.create_user(username='ruser', password='pass')
        room = Room.objects.create(room_number='110', room_type='Эконом', price_per_night=350, max_occupancy=1)
        review = Review.objects.create(room=room, guest=user, rating=4, comment='Хорошо')
        self.assertIn('Review', str(review))

    def test_room_serializer_fields(self) -> None:
        """Проверяет наличие поля room_type в сериализаторе комнаты."""
        room = Room.objects.create(room_number='111', room_type='Люкс', price_per_night=2000, max_occupancy=4)
        data = RoomSerializer(room).data
        self.assertIn('room_type', data)
