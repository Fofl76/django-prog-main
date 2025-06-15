# bookings/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count, Q, Sum, F, ExpressionWrapper, DecimalField, IntegerField, DurationField, Case, When, Value
from datetime import timedelta
from .managers import RoomManager, BookingManager
from django.urls import reverse

class Amenity(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']  # Сортировка удобств по алфавиту
        verbose_name = 'Удобство'
        verbose_name_plural = 'Удобства'

    def get_absolute_url(self):
        """Получить абсолютный URL удобства"""
        return reverse('amenity-detail', kwargs={'pk': self.pk})

    def get_rooms_url(self):
        """Получить URL для просмотра комнат с этим удобством"""
        return reverse('amenity-rooms', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)
    price_per_night = models.DecimalField(max_digits=6, decimal_places=2)
    max_occupancy = models.IntegerField()
    amenities = models.ManyToManyField('Amenity', blank=True, related_name='rooms')
    is_available = models.BooleanField(default=True)
    
    # Добавляем менеджеры
    objects = models.Manager()  # Стандартный менеджер
    rooms = RoomManager()  # Пользовательский менеджер
    
    class Meta:
        ordering = ['room_number']  # Сортировка комнат по номеру
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'

    def get_absolute_url(self):
        """Получить абсолютный URL комнаты"""
        return reverse('room-detail', kwargs={'pk': self.pk})

    def get_booking_url(self):
        """Получить URL для бронирования комнаты"""
        return reverse('book_room', kwargs={'room_id': self.pk})

    def get_reviews_url(self):
        """Получить URL для просмотра отзывов о комнате"""
        return reverse('room-reviews', kwargs={'pk': self.pk})

    def get_amenities_url(self):
        """Получить URL для просмотра удобств комнаты"""
        return reverse('room-amenities', kwargs={'pk': self.pk})

    @classmethod
    def get_rooms_by_price(cls, ascending=True):
        """Получить комнаты, отсортированные по цене"""
        return cls.objects.all().order_by('price_per_night' if ascending else '-price_per_night')

    @classmethod
    def get_rooms_by_occupancy(cls):
        """Получить комнаты, отсортированные по вместимости (по убыванию)"""
        return cls.objects.all().order_by('-max_occupancy')

    @classmethod
    def get_rooms_by_popularity(cls):
        """Получить комнаты, отсортированные по количеству бронирований"""
        return cls.objects.annotate(
            booking_count=Count('bookings')
        ).order_by('-booking_count')

    @classmethod
    def get_top_rated_rooms(cls):
        """Получить комнаты, отсортированные по среднему рейтингу"""
        return cls.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')

    @classmethod
    def get_available_rooms(cls, check_in, check_out):
        """Получить список доступных комнат на указанные даты"""
        return cls.objects.exclude(
            Q(bookings__status='confirmed') &
            Q(bookings__check_in__lte=check_out) &
            Q(bookings__check_out__gte=check_in)
        ).filter(is_available=True).order_by('price_per_night')  # Сортировка по возрастанию цены

    @classmethod
    def get_rooms_by_price_range(cls, min_price=None, max_price=None):
        """Получить комнаты в указанном ценовом диапазоне"""
        rooms = cls.objects.all()
        if min_price is not None:
            rooms = rooms.exclude(price_per_night__lt=min_price)
        if max_price is not None:
            rooms = rooms.exclude(price_per_night__gt=max_price)
        return rooms

    @classmethod
    def get_rooms_without_amenity(cls, amenity_name):
        """Получить комнаты, в которых нет указанного удобства"""
        return cls.objects.exclude(amenities__name=amenity_name)

    @classmethod
    def get_rooms_without_reviews(cls):
        """Получить комнаты без отзывов"""
        return cls.objects.exclude(reviews__isnull=False)

    @classmethod
    def get_rooms_with_high_rated_reviews(cls, min_rating=4):
        """Получить комнаты с высокорейтинговыми отзывами"""
        return cls.objects.filter(reviews__rating__gte=min_rating).distinct()

    @classmethod
    def get_rooms_with_recent_bookings(cls, days=30):
        """Получить комнаты с недавними бронированиями"""
        recent_date = timezone.now() - timedelta(days=days)
        return cls.objects.filter(bookings__created_at__gte=recent_date).distinct()

    @classmethod
    def get_rooms_by_guest_country(cls, country):
        """Получить комнаты, забронированные гостями из определенной страны"""
        return cls.objects.filter(bookings__guest__guest_profile__country=country).distinct()

    @classmethod
    def get_rooms_with_specific_amenities(cls, amenity_names):
        """Получить комнаты с определенными удобствами"""
        return cls.objects.filter(amenities__name__in=amenity_names).distinct()

    @classmethod
    def get_rooms_by_review_keywords(cls, keyword):
        """Получить комнаты с отзывами, содержащими определенные ключевые слова"""
        return cls.objects.filter(reviews__comment__icontains=keyword).distinct()

    @classmethod
    def get_rooms_with_long_stays(cls, min_days=7):
        """Получить комнаты с длительными бронированиями"""
        from django.db.models import F, ExpressionWrapper, DurationField
        return cls.objects.annotate(
            stay_duration=ExpressionWrapper(
                F('bookings__check_out') - F('bookings__check_in'),
                output_field=DurationField()
            )
        ).filter(stay_duration__gte=timedelta(days=min_days)).distinct()

    @classmethod
    def get_rooms_with_repeat_guests(cls):
        """Получить комнаты с повторными бронированиями от одних и тех же гостей"""
        from django.db.models import Count
        return cls.objects.annotate(
            repeat_guests=Count('bookings__guest', distinct=True)
        ).filter(repeat_guests__gt=1)

    def get_current_booking(self):
        """Получить текущее активное бронирование комнаты"""
        today = timezone.now().date()
        return self.bookings.filter(
            check_in__lte=today,
            check_out__gte=today,
            status='confirmed'
        ).first()

    def get_upcoming_bookings(self):
        """Получить предстоящие бронирования комнаты"""
        today = timezone.now().date()
        return self.bookings.filter(
            check_in__gt=today,
            status='confirmed'
        ).order_by('check_in')

    def get_average_rating(self):
        """Получить средний рейтинг комнаты"""
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    def get_amenities_list(self):
        """Получить список удобств комнаты"""
        return list(self.amenities.values_list('name', flat=True))

    def get_future_bookings(self):
        """Получить будущие бронирования комнаты, отсортированные по дате заезда"""
        return self.bookings.exclude(
            Q(check_in__lt=timezone.now().date()) |
            Q(status='cancelled')
        ).order_by('check_in')

    def get_room_reviews(self):
        """Получить отзывы о комнате, отсортированные по дате"""
        return self.reviews.all().order_by('-review_date')

    def get_guest_reviews(self, guest_id):
        """Получить отзывы конкретного гостя о комнате"""
        return self.reviews.filter(guest__id=guest_id).order_by('-review_date')

    def get_bookings_by_status(self, status):
        """Получить бронирования комнаты с определенным статусом"""
        return self.bookings.filter(status=status).order_by('-created_at')

    def get_future_bookings_with_guest_info(self):
        """Получить будущие бронирования с информацией о гостях"""
        return self.bookings.select_related('guest__guest_profile').filter(
            check_in__gt=timezone.now().date()
        ).order_by('check_in')

    @classmethod
    def get_room_statistics(cls):
        """
        Комплексная статистика по комнатам
        
        Возвращает статистику по каждой комнате:
        - Средний рейтинг
        - Количество бронирований
        - Общая выручка
        - Средняя продолжительность проживания
        - Процент отмененных бронирований
        """
        return cls.objects.annotate(
            # Средний рейтинг комнаты
            avg_rating=Avg('reviews__rating'),
            
            # Общее количество бронирований
            total_bookings=Count('bookings'),
            
            # Количество отмененных бронирований
            cancelled_bookings=Count(
                'bookings',
                filter=Q(bookings__status='cancelled')
            ),
            
            # Процент отмененных бронирований
            cancellation_rate=ExpressionWrapper(
                Case(
                    When(total_bookings=0, then=Value(0)),
                    default=F('cancelled_bookings') * 100.0 / F('total_bookings')
                ),
                output_field=DecimalField()
            ),
            
            # Общая выручка
            total_revenue=Sum(
                ExpressionWrapper(
                    F('bookings__check_out') - F('bookings__check_in'),
                    output_field=IntegerField()
                ) * F('price_per_night'),
                filter=Q(bookings__status='confirmed')
            ),
            
            # Средняя продолжительность проживания
            avg_stay_duration=Avg(
                ExpressionWrapper(
                    F('bookings__check_out') - F('bookings__check_in'),
                    output_field=DurationField()
                ),
                filter=Q(bookings__status='confirmed')
            )
        )

    @classmethod
    def get_popular_room_types(cls):
        """
        Анализ популярности типов комнат
        
        Возвращает статистику по типам комнат:
        - Количество комнат данного типа
        - Общее количество бронирований
        - Средняя цена
        - Средний рейтинг
        - Общая выручка
        """
        return cls.objects.values('room_type').annotate(
            # Количество комнат данного типа
            rooms_count=Count('id'),
            
            # Количество бронирований
            bookings_count=Count('bookings', filter=Q(bookings__status='confirmed')),
            
            # Средняя цена за ночь
            avg_price=Avg('price_per_night'),
            
            # Средний рейтинг
            avg_rating=Avg('reviews__rating'),
            
            # Общая выручка по типу комнат
            total_revenue=Sum(
                ExpressionWrapper(
                    F('bookings__check_out') - F('bookings__check_in'),
                    output_field=IntegerField()
                ) * F('price_per_night'),
                filter=Q(bookings__status='confirmed')
            )
        ).order_by('-bookings_count')

    @classmethod
    def get_monthly_statistics(cls, year, month):
        """
        Месячная статистика по комнатам
        
        Возвращает статистику за указанный месяц:
        - Количество бронирований
        - Общая выручка
        - Средняя загрузка
        - Средний рейтинг
        - Количество отзывов
        """
        start_date = timezone.datetime(year, month, 1)
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1)
        else:
            end_date = timezone.datetime(year, month + 1, 1)

        return cls.objects.annotate(
            # Количество бронирований за месяц
            monthly_bookings=Count(
                'bookings',
                filter=Q(
                    bookings__check_in__gte=start_date,
                    bookings__check_in__lt=end_date,
                    bookings__status='confirmed'
                )
            ),
            
            # Выручка за месяц
            monthly_revenue=Sum(
                ExpressionWrapper(
                    F('bookings__check_out') - F('bookings__check_in'),
                    output_field=IntegerField()
                ) * F('price_per_night'),
                filter=Q(
                    bookings__check_in__gte=start_date,
                    bookings__check_in__lt=end_date,
                    bookings__status='confirmed'
                )
            ),
            
            # Количество дней занятости в месяце
            occupied_days=Count(
                'bookings__check_in',
                filter=Q(
                    bookings__check_in__gte=start_date,
                    bookings__check_in__lt=end_date,
                    bookings__status='confirmed'
                ),
                distinct=True
            ),
            
            # Средняя загрузка (процент занятых дней)
            occupancy_rate=ExpressionWrapper(
                F('occupied_days') * 100.0 / Value(30),  # примерно 30 дней в месяце
                output_field=DecimalField()
            ),
            
            # Средний рейтинг за месяц
            monthly_rating=Avg(
                'reviews__rating',
                filter=Q(
                    reviews__review_date__gte=start_date,
                    reviews__review_date__lt=end_date
                )
            ),
            
            # Количество отзывов за месяц
            reviews_count=Count(
                'reviews',
                filter=Q(
                    reviews__review_date__gte=start_date,
                    reviews__review_date__lt=end_date
                )
            )
        )

    def __str__(self):
        return f"Комната {self.room_number} ({self.room_type})"

class Guest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['last_name', 'first_name'] 
        verbose_name = 'Гость'
        verbose_name_plural = 'Гости'

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено')
    ]

    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    guests_count = models.IntegerField(default=1)

    # Добавляем менеджеры
    objects = models.Manager()  # Стандартный менеджер
    bookings = BookingManager()  # Пользовательский менеджер

    class Meta:
        ordering = ['-created_at', 'check_in']  
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out__gt=models.F('check_in')),
                name='valid_booking_dates'
            )
        ]

    def get_absolute_url(self):
        """Получить абсолютный URL бронирования"""
        return reverse('booking-detail', kwargs={'pk': self.pk})

    def get_cancel_url(self):
        """Получить URL для отмены бронирования"""
        return reverse('cancel-booking', kwargs={'pk': self.pk})

    def get_modify_url(self):
        """Получить URL для изменения бронирования"""
        return reverse('modify-booking', kwargs={'pk': self.pk})

    def get_payment_url(self):
        """Получить URL для оплаты бронирования"""
        return reverse('booking-payment', kwargs={'pk': self.pk})

    def total_price(self):
        """Вычисляет общую стоимость бронирования"""
        if not self.check_in or not self.check_out or not self.room:
            return 0
        days = (self.check_out - self.check_in).days
        return self.room.price_per_night * days

    total_price.short_description = 'Общая стоимость'

    def is_active(self):
        """Проверяет, активно ли бронирование на текущую дату"""
        today = timezone.now().date()
        return self.check_in <= today <= self.check_out and self.status == 'confirmed'

    def is_upcoming(self):
        """Проверяет, предстоит ли заезд"""
        today = timezone.now().date()
        return self.check_in > today and self.status == 'confirmed'

    def can_be_cancelled(self):
        """Можно ли отменить бронирование (за 24 часа до заезда)"""
        cancellation_deadline = timezone.now() + timezone.timedelta(hours=24)
        check_in_datetime = timezone.make_aware(
            timezone.datetime.combine(self.check_in, timezone.datetime.min.time())
        )
        return check_in_datetime > cancellation_deadline

    def get_guest_bookings_history(self):
        """Получить историю бронирований гостя"""
        return self.guest.bookings.exclude(id=self.id).order_by('-created_at')

    def get_room_bookings(self):
        """Получить все бронирования этой комнаты"""
        return self.room.bookings.exclude(id=self.id).order_by('check_in')

    def get_guest_payments(self):
        """Получить все платежи гостя по этому бронированию"""
        return self.payments.all().order_by('-payment_date')

    def __str__(self):
        return f"Booking {self.id} - {self.guest.username} - {self.room.room_number}"

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Ожидает оплаты'),
        ('completed', 'Оплачено'),
        ('failed', 'Ошибка оплаты'),
        ('refunded', 'Возвращено')
    ]

    PAYMENT_METHODS = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличные'),
        ('transfer', 'Банковский перевод')
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='card')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    class Meta:
        ordering = ['-payment_date']  # Сортировка платежей по дате (сначала новые)
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

    def get_booking_payments(self):
        """Получить все платежи по этому бронированию"""
        return self.booking.payments.exclude(id=self.id)

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id}"

class Review(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-review_date', '-rating']  # Сортировка отзывов: сначала новые, потом по рейтингу
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        # Добавляем ограничение, чтобы один гость мог оставить только один отзыв для комнаты
        constraints = [
            models.UniqueConstraint(
                fields=['guest', 'room'],
                name='unique_guest_room_review'
            )
        ]

    def get_absolute_url(self):
        """Получить абсолютный URL отзыва"""
        return reverse('review-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        """Получить URL для редактирования отзыва"""
        return reverse('edit-review', kwargs={'pk': self.pk})

    def get_guest_other_reviews(self):
        """Получить другие отзывы этого гостя"""
        return self.guest.reviews.exclude(id=self.id)

    def get_room_reviews(self):
        """Получить все отзывы по этой комнате"""
        return self.room.reviews.exclude(id=self.id)

    def __str__(self):
        return f"Review {self.id} - {self.room} by {self.guest.username if self.guest else 'Anonymous'}"
