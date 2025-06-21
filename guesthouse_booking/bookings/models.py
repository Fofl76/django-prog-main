# bookings/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import (
    Avg, Count, Q, Sum, F, ExpressionWrapper, 
    DecimalField, IntegerField, DurationField, 
    Case, When, Value
)
from datetime import timedelta
from .managers import RoomManager, BookingManager
from django.urls import reverse
from django.core.cache import cache

class Amenity(models.Model):
    """Модель удобства для комнаты."""
    name: str = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = 'Удобство'
        verbose_name_plural = 'Удобства'
        indexes = [
            models.Index(fields=['name']),
        ]

    def get_absolute_url(self) -> str:
        """Возвращает абсолютный URL для удобства."""
        return reverse('amenity-detail', kwargs={'pk': self.pk})

    def get_rooms_url(self):
        return reverse('amenity-rooms', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        """Строковое представление удобства."""
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50, db_index=True)
    price_per_night = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    max_occupancy = models.IntegerField()
    amenities = models.ManyToManyField('Amenity', blank=True, related_name='rooms')
    special_offers = models.ManyToManyField(
        'SpecialOffer', 
        through='RoomSpecialOffer',
        blank=True, 
        related_name='rooms'
    )
    is_available = models.BooleanField(default=True, db_index=True)
    
    # Новые поля для файлов
    photo = models.ImageField(
        upload_to='rooms/photos/', 
        blank=True, 
        null=True,
        verbose_name='Фото комнаты'
    )
    floor_plan = models.FileField(
        upload_to='rooms/floor_plans/', 
        blank=True, 
        null=True,
        verbose_name='План этажа',
        help_text='PDF или изображение плана этажа'
    )
    documents = models.FileField(
        upload_to='rooms/documents/', 
        blank=True, 
        null=True,
        verbose_name='Документы',
        help_text='Дополнительные документы (сертификаты, инструкции)'
    )
    
    objects = models.Manager()
    rooms = RoomManager()
    
    class Meta:
        ordering = ['room_number']
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
        indexes = [
            models.Index(fields=['room_number']),
            models.Index(fields=['price_per_night']),
            models.Index(fields=['is_available']),
            models.Index(fields=['room_type', 'is_available']),
        ]

    def get_absolute_url(self):
        return reverse('room-detail', kwargs={'pk': self.pk})

    def get_booking_url(self):
        return reverse('book_room', kwargs={'room_id': self.pk})

    def get_reviews_url(self):
        return reverse('room-reviews', kwargs={'pk': self.pk})

    def get_amenities_url(self):
        return reverse('room-amenities', kwargs={'pk': self.pk})

    @classmethod
    def get_rooms_by_price(cls, ascending=True):
        return cls.objects.all().order_by('price_per_night' if ascending else '-price_per_night')

    @classmethod
    def get_rooms_by_occupancy(cls):
        return cls.objects.all().order_by('-max_occupancy')

    @classmethod
    def get_rooms_by_popularity(cls):
        return cls.objects.annotate(
            booking_count=Count('bookings')
        ).order_by('-booking_count')

    @classmethod
    def get_top_rated_rooms(cls):
        return cls.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')

    @classmethod
    def get_available_rooms(cls, check_in, check_out):
        return cls.objects.filter(is_available=True).exclude(
            bookings__status='confirmed',
            bookings__check_in__lt=check_out,
            bookings__check_out__gt=check_in
        ).distinct().order_by('price_per_night')

    @classmethod
    def get_rooms_by_price_range(cls, min_price=None, max_price=None):
        queryset = cls.objects.all()
        if min_price is not None:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price_per_night__lte=max_price)
        return queryset

    @classmethod
    def get_rooms_without_amenity(cls, amenity_name):
        return cls.objects.exclude(amenities__name=amenity_name)

    @classmethod
    def get_rooms_without_reviews(cls):
        return cls.objects.filter(reviews__isnull=True)

    @classmethod
    def get_rooms_with_high_rated_reviews(cls, min_rating=4):
        return cls.objects.filter(reviews__rating__gte=min_rating).distinct()

    @classmethod
    def get_rooms_with_recent_bookings(cls, days=30):
        recent_date = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            bookings__created_at__gte=recent_date
        ).distinct().select_related(None).prefetch_related(None)

    @classmethod
    def get_rooms_by_guest_country(cls, country):
        return cls.objects.filter(
            bookings__guest__guest_profile__country=country
        ).distinct().select_related(None)

    @classmethod
    def get_rooms_with_specific_amenities(cls, amenity_names):
        return cls.objects.filter(
            amenities__name__in=amenity_names
        ).distinct().prefetch_related('amenities')

    @classmethod
    def get_rooms_by_review_keywords(cls, keyword):
        return cls.objects.filter(
            reviews__comment__icontains=keyword
        ).distinct().select_related(None)

    @classmethod
    def get_rooms_with_long_stays(cls, min_days=7):
        return cls.objects.annotate(
            stay_duration=ExpressionWrapper(
                F('bookings__check_out') - F('bookings__check_in'),
                output_field=DurationField()
            )
        ).filter(
            stay_duration__gte=timedelta(days=min_days)
        ).distinct()

    @classmethod
    def get_rooms_with_repeat_guests(cls):
        return cls.objects.annotate(
            repeat_guests=Count('bookings__guest', distinct=True)
        ).filter(repeat_guests__gt=1)

    def get_current_booking(self):
        today = timezone.now().date()
        return self.bookings.filter(
            check_in__lte=today,
            check_out__gte=today,
            status='confirmed'
        ).select_related('guest').first()

    def get_upcoming_bookings(self):
        today = timezone.now().date()
        return self.bookings.filter(
            check_in__gt=today,
            status='confirmed'
        ).select_related('guest').order_by('check_in')

    def get_average_rating(self):
        cache_key = f'room_{self.id}_avg_rating'
        avg_rating = cache.get(cache_key)
        
        if avg_rating is None:
            avg_rating = self.reviews.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0
            cache.set(cache_key, avg_rating, timeout=60*60)
        
        return avg_rating

    def get_amenities_list(self):
        return list(self.amenities.values_list('name', flat=True))

    def get_future_bookings(self):
        return self.bookings.exclude(
            Q(check_in__lt=timezone.now().date()) |
            Q(status='cancelled')
        ).select_related('guest').order_by('check_in')

    def get_room_reviews(self):
        return self.reviews.all().select_related('guest').only(
            'rating', 'comment', 'review_date', 'guest__username'
        ).order_by('-review_date')

    def get_active_special_offers(self):
        """Возвращает активные специальные предложения для комнаты"""
        today = timezone.now().date()
        return self.room_special_offers.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).select_related('special_offer').order_by('-discount_percentage')

    def get_current_price_with_discount(self):
        """Возвращает текущую цену с учетом активных скидок"""
        active_offers = self.get_active_special_offers()
        if active_offers.exists():
            # Берем предложение с максимальной скидкой
            best_offer = active_offers.first()
            return best_offer.get_discounted_price()
        return self.price_per_night

    def get_max_discount_percentage(self):
        """Возвращает максимальный процент скидки среди активных предложений"""
        active_offers = self.get_active_special_offers()
        if active_offers.exists():
            return active_offers.aggregate(
                max_discount=models.Max('discount_percentage')
            )['max_discount']
        return 0

    def has_active_special_offers(self):
        """Проверяет, есть ли у комнаты активные специальные предложения"""
        return self.get_active_special_offers().exists()

    def get_special_offers_history(self):
        """Возвращает историю всех специальных предложений для комнаты"""
        return self.room_special_offers.select_related('special_offer').order_by('-created_at')

    def add_special_offer(self, special_offer, start_date, end_date, discount_percentage=0):
        """Добавляет специальное предложение к комнате"""
        return self.room_special_offers.create(
            special_offer=special_offer,
            start_date=start_date,
            end_date=end_date,
            discount_percentage=discount_percentage
        )

    def remove_special_offer(self, special_offer):
        """Удаляет специальное предложение с комнаты"""
        self.room_special_offers.filter(special_offer=special_offer).delete()

    @classmethod
    def get_rooms_with_special_offers(cls):
        """Возвращает комнаты с активными специальными предложениями"""
        today = timezone.now().date()
        return cls.objects.filter(
            room_special_offers__is_active=True,
            room_special_offers__start_date__lte=today,
            room_special_offers__end_date__gte=today
        ).distinct().prefetch_related('room_special_offers__special_offer')

    @classmethod
    def get_rooms_by_discount_range(cls, min_discount=0, max_discount=100):
        """Возвращает комнаты с скидками в указанном диапазоне"""
        today = timezone.now().date()
        return cls.objects.filter(
            room_special_offers__is_active=True,
            room_special_offers__start_date__lte=today,
            room_special_offers__end_date__gte=today,
            room_special_offers__discount_percentage__gte=min_discount,
            room_special_offers__discount_percentage__lte=max_discount
        ).distinct().prefetch_related('room_special_offers__special_offer')

    def get_guest_reviews(self, guest_id):
        return self.reviews.filter(
            guest__id=guest_id
        ).only('rating', 'comment', 'review_date').order_by('-review_date')

    def get_bookings_by_status(self, status):
        return self.bookings.filter(
            status=status
        ).select_related('guest').order_by('-created_at')

    def get_future_bookings_with_guest_info(self):
        return self.bookings.select_related(
            'guest', 'guest__guest_profile'
        ).filter(
            check_in__gt=timezone.now().date()
        ).order_by('check_in')

    @classmethod
    def get_room_statistics(cls):
        return cls.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            total_bookings=Count('bookings'),
            cancelled_bookings=Count(
                'bookings',
                filter=Q(bookings__status='cancelled')
            ),
            cancellation_rate=Case(
                When(total_bookings=0, then=Value(0)),
                default=F('cancelled_bookings') * 100.0 / F('total_bookings'),
                output_field=DecimalField(decimal_places=2)
            ),
            total_revenue=Sum(
                ExpressionWrapper(
                    F('bookings__check_out') - F('bookings__check_in'),
                    output_field=IntegerField()
                ) * F('price_per_night'),
                filter=Q(bookings__status='confirmed')
            ),
            avg_stay_duration=Avg(
                F('bookings__check_out') - F('bookings__check_in'),
                filter=Q(bookings__status='confirmed'),
                output_field=DurationField()
            )
        ).only('room_number', 'room_type', 'price_per_night')

    @classmethod
    def get_popular_room_types(cls):
        return cls.objects.values('room_type').annotate(
            rooms_count=Count('id'),
            bookings_count=Count('bookings', filter=Q(bookings__status='confirmed')),
            avg_price=Avg('price_per_night'),
            avg_rating=Avg('reviews__rating'),
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
        start_date = timezone.datetime(year, month, 1)
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1)
        else:
            end_date = timezone.datetime(year, month + 1, 1)

        return cls.objects.annotate(
            monthly_bookings=Count(
                'bookings',
                filter=Q(
                    bookings__check_in__gte=start_date,
                    bookings__check_in__lt=end_date,
                    bookings__status='confirmed'
                )
            ),
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
            occupied_days=Count(
                'bookings__check_in',
                filter=Q(
                    bookings__check_in__gte=start_date,
                    bookings__check_in__lt=end_date,
                    bookings__status='confirmed'
                ),
                distinct=True
            ),
            occupancy_rate=ExpressionWrapper(
                F('occupied_days') * 100.0 / Value(30),
                output_field=DecimalField(decimal_places=2)
            ),
            monthly_rating=Avg(
                'reviews__rating',
                filter=Q(
                    reviews__review_date__gte=start_date,
                    reviews__review_date__lt=end_date
                )
            ),
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

class UserRole(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'

    def __str__(self):
        return self.name

class Guest(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='guest_profile'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    role = models.ForeignKey(
        UserRole, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Новые поля для файлов
    passport_scan = models.FileField(
        upload_to='guests/passports/', 
        blank=True, 
        null=True,
        verbose_name='Скан паспорта',
        help_text='Скан или фото паспорта'
    )
    id_document = models.FileField(
        upload_to='guests/id_documents/', 
        blank=True, 
        null=True,
        verbose_name='Удостоверение личности',
        help_text='Водительские права, военный билет и т.д.'
    )
    additional_documents = models.FileField(
        upload_to='guests/additional_docs/', 
        blank=True, 
        null=True,
        verbose_name='Дополнительные документы',
        help_text='Другие документы гостя'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Гость'
        verbose_name_plural = 'Гости'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['last_name', 'first_name']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено')
    ]

    guest = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    check_in = models.DateField(db_index=True)
    check_out = models.DateField(db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, 
        choices=BOOKING_STATUS, 
        default='pending',
        db_index=True
    )
    guests_count = models.IntegerField(default=1)
    
    # Новые поля для файлов
    contract = models.FileField(
        upload_to='bookings/contracts/', 
        blank=True, 
        null=True,
        verbose_name='Договор',
        help_text='Сканированный договор бронирования'
    )
    receipt = models.FileField(
        upload_to='bookings/receipts/', 
        blank=True, 
        null=True,
        verbose_name='Квитанция',
        help_text='Квитанция об оплате'
    )
    additional_files = models.FileField(
        upload_to='bookings/additional_files/', 
        blank=True, 
        null=True,
        verbose_name='Дополнительные файлы',
        help_text='Другие документы, связанные с бронированием'
    )

    objects = models.Manager()
    bookings = BookingManager()

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
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['check_in', 'check_out']),
            models.Index(fields=['guest', 'room']),
        ]

    def get_absolute_url(self):
        return reverse('booking-detail', kwargs={'pk': self.pk})

    def get_cancel_url(self):
        return reverse('cancel-booking', kwargs={'pk': self.pk})

    def get_modify_url(self):
        return reverse('modify-booking', kwargs={'pk': self.pk})

    def get_payment_url(self):
        return reverse('booking-payment', kwargs={'pk': self.pk})

    def total_price(self):
        if not all([self.check_in, self.check_out, self.room]):
            return 0
        days = (self.check_out - self.check_in).days
        return self.room.price_per_night * days

    def is_active(self):
        today = timezone.now().date()
        return (
            self.check_in <= today <= self.check_out 
            and self.status == 'confirmed'
        )

    def is_upcoming(self):
        today = timezone.now().date()
        return self.check_in > today and self.status == 'confirmed'

    def can_be_cancelled(self):
        cancellation_deadline = timezone.now() + timezone.timedelta(hours=24)
        check_in_datetime = timezone.make_aware(
            timezone.datetime.combine(self.check_in, timezone.datetime.min.time())
        )
        return check_in_datetime > cancellation_deadline

    def get_guest_bookings_history(self):
        return self.guest.bookings.exclude(
            id=self.id
        ).select_related('room').order_by('-created_at')

    def get_room_bookings(self):
        return self.room.bookings.exclude(
            id=self.id
        ).select_related('guest').order_by('check_in')

    def get_guest_payments(self):
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

    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField(default=timezone.now, db_index=True)
    payment_method = models.CharField(
        max_length=50, 
        choices=PAYMENT_METHODS, 
        default='card'
    )
    status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS, 
        default='pending',
        db_index=True
    )
    
    # Новые поля для файлов
    payment_receipt = models.FileField(
        upload_to='payments/receipts/', 
        blank=True, 
        null=True,
        verbose_name='Квитанция об оплате',
        help_text='Скан или фото квитанции'
    )
    bank_statement = models.FileField(
        upload_to='payments/bank_statements/', 
        blank=True, 
        null=True,
        verbose_name='Банковская выписка',
        help_text='Выписка по банковскому переводу'
    )
    refund_document = models.FileField(
        upload_to='payments/refunds/', 
        blank=True, 
        null=True,
        verbose_name='Документ о возврате',
        help_text='Документ о возврате средств'
    )

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
        ]

    def get_booking_payments(self):
        return self.booking.payments.exclude(id=self.id)

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id}"

class Review(models.Model):
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    guest = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        null=True, 
        blank=True
    )
    rating = models.IntegerField()
    comment = models.TextField()
    review_date = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-review_date', '-rating']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['guest', 'room'],
                name='unique_guest_room_review'
            )
        ]
        indexes = [
            models.Index(fields=['room', 'rating']),
            models.Index(fields=['guest', 'review_date']),
        ]

    def get_absolute_url(self):
        return reverse('review-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('edit-review', kwargs={'pk': self.pk})

    def get_guest_other_reviews(self):
        return self.guest.reviews.exclude(
            id=self.id
        ).select_related('room').only(
            'rating', 'comment', 'review_date', 'room__room_number'
        ).order_by('-review_date')

    def get_room_reviews(self):
        return self.room.reviews.exclude(
            id=self.id
        ).select_related('guest').only(
            'rating', 'comment', 'review_date', 'guest__username'
        ).order_by('-review_date')

    def __str__(self):
        return f"Review {self.id} - {self.room} by {self.guest.username if self.guest else 'Anonymous'}"

class SliderImage(models.Model):
    image = models.ImageField(upload_to='slider_images/')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Изображение слайдера'
        verbose_name_plural = 'Изображения слайдера'

    def __str__(self):
        return self.title or f'Слайд {self.id}'

class SpecialOffer(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(upload_to='special_offers/', verbose_name='Изображение')
    short_description = models.TextField(verbose_name='Краткое описание')
    full_description = models.TextField(verbose_name='Полное описание')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name='Цена'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Специальное предложение'
        verbose_name_plural = 'Специальные предложения'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

    def get_absolute_url(self):
        return reverse('special-offer-detail', kwargs={'pk': self.pk})

    def get_rooms_url(self):
        return reverse('special-offer-rooms', kwargs={'pk': self.pk})

    def get_active_rooms(self):
        """Возвращает комнаты с активным применением этого предложения"""
        today = timezone.now().date()
        return self.rooms.filter(
            room_special_offers__is_active=True,
            room_special_offers__start_date__lte=today,
            room_special_offers__end_date__gte=today
        ).distinct().prefetch_related('room_special_offers')

    def get_all_applied_rooms(self):
        """Возвращает все комнаты, к которым применялось это предложение"""
        return self.rooms.distinct().prefetch_related('room_special_offers')

    def apply_to_room(self, room, start_date, end_date, discount_percentage=0):
        """Применяет предложение к комнате"""
        return self.room_special_offers.create(
            room=room,
            start_date=start_date,
            end_date=end_date,
            discount_percentage=discount_percentage
        )

    def remove_from_room(self, room):
        """Удаляет предложение с комнаты"""
        self.room_special_offers.filter(room=room).delete()

    def get_application_history(self):
        """Возвращает историю применения предложения"""
        return self.room_special_offers.select_related('room').order_by('-created_at')

    def get_total_applications_count(self):
        """Возвращает общее количество применений предложения"""
        return self.room_special_offers.count()

    def get_active_applications_count(self):
        """Возвращает количество активных применений предложения"""
        today = timezone.now().date()
        return self.room_special_offers.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).count()

    @classmethod
    def get_offers_with_rooms(cls):
        """Возвращает предложения, которые применяются к комнатам"""
        return cls.objects.filter(
            room_special_offers__isnull=False
        ).distinct().prefetch_related('room_special_offers__room')

    @classmethod
    def get_popular_offers(cls):
        """Возвращает самые популярные предложения по количеству применений"""
        return cls.objects.annotate(
            applications_count=models.Count('room_special_offers')
        ).order_by('-applications_count')

    def __str__(self):
        return self.title

class RoomSpecialOffer(models.Model):
    """
    Промежуточная модель для связи Room и SpecialOffer с дополнительными данными
    """
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE,
        related_name='room_special_offers',
        verbose_name='Комната'
    )
    special_offer = models.ForeignKey(
        SpecialOffer, 
        on_delete=models.CASCADE,
        related_name='room_special_offers',
        verbose_name='Специальное предложение'
    )
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        verbose_name='Процент скидки'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Связь комнаты и специального предложения'
        verbose_name_plural = 'Связи комнат и специальных предложений'
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'special_offer'],
                name='unique_room_special_offer'
            ),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='valid_offer_dates'
            )
        ]
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active']),
            models.Index(fields=['discount_percentage']),
        ]

    def is_currently_active(self):
        """Проверяет, активно ли предложение в данный момент"""
        today = timezone.now().date()
        return (
            self.is_active and 
            self.start_date <= today <= self.end_date
        )

    def get_discounted_price(self):
        """Возвращает цену со скидкой"""
        if self.discount_percentage > 0:
            discount_amount = self.room.price_per_night * (self.discount_percentage / 100)
            return self.room.price_per_night - discount_amount
        return self.room.price_per_night

    def get_discount_amount(self):
        """Возвращает сумму скидки"""
        if self.discount_percentage > 0:
            return self.room.price_per_night * (self.discount_percentage / 100)
        return 0

    def get_absolute_url(self):
        return reverse('room-special-offer-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.room.room_number} - {self.special_offer.title}"

class Document(models.Model):
    """Модель для централизованного управления документами"""
    
    DOCUMENT_TYPES = [
        ('contract', 'Договор'),
        ('receipt', 'Квитанция'),
        ('passport', 'Паспорт'),
        ('id_card', 'Удостоверение личности'),
        ('photo', 'Фото'),
        ('plan', 'План'),
        ('certificate', 'Сертификат'),
        ('statement', 'Выписка'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    file = models.FileField(
        upload_to='documents/%Y/%m/%d/', 
        verbose_name='Файл'
    )
    file_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPES, 
        default='other',
        verbose_name='Тип документа'
    )
    
    # Связи с другими моделями
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='room_documents',
        verbose_name='Комната'
    )
    guest = models.ForeignKey(
        Guest, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='guest_documents',
        verbose_name='Гость'
    )
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='booking_documents',
        verbose_name='Бронирование'
    )
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='payment_documents',
        verbose_name='Платёж'
    )
    
    is_public = models.BooleanField(
        default=False, 
        verbose_name='Публичный доступ',
        help_text='Доступен ли документ для просмотра гостями'
    )
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Загрузил'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        indexes = [
            models.Index(fields=['file_type']),
            models.Index(fields=['is_public']),
            models.Index(fields=['uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"
    
    def get_file_extension(self):
        """Возвращает расширение файла"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return ''
    
    def get_file_size(self):
        """Возвращает размер файла в байтах"""
        if self.file and hasattr(self.file, 'size'):
            return self.file.size
        return 0
    
    def get_file_size_display(self):
        """Возвращает размер файла в читаемом формате"""
        size = self.get_file_size()
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def is_image(self):
        """Проверяет, является ли файл изображением"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        return self.get_file_extension() in image_extensions
    
    def is_pdf(self):
        """Проверяет, является ли файл PDF"""
        return self.get_file_extension() == 'pdf'
    
    def get_download_url(self):
        """Возвращает URL для скачивания файла"""
        return self.file.url if self.file else None
    
    def get_preview_url(self):
        """Возвращает URL для предварительного просмотра"""
        if self.is_image():
            return self.file.url
        elif self.is_pdf():
            return self.file.url
        return None