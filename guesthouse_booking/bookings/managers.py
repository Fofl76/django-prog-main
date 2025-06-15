# bookings/managers.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, DurationField

class RoomManager(models.Manager):
    def available_rooms(self, check_in, check_out):
        """Получить доступные комнаты на указанные даты"""
        return self.filter(is_available=True).exclude(
            Q(bookings__status='confirmed') &
            Q(bookings__check_in__lte=check_out) &
            Q(bookings__check_out__gte=check_in)
        )

    def luxury_rooms(self, min_price=5000):
        """Получить люкс-комнаты (с ценой выше указанной)"""
        return self.filter(price_per_night__gte=min_price)

    def budget_rooms(self, max_price=2000):
        """Получить бюджетные комнаты (с ценой ниже указанной)"""
        return self.filter(price_per_night__lte=max_price)

    def popular_rooms(self, min_bookings=5):
        """Получить популярные комнаты (с количеством бронирований выше указанного)"""
        return self.annotate(
            booking_count=Count('bookings')
        ).filter(booking_count__gte=min_bookings)

    def top_rated(self, min_rating=4.0):
        """Получить высокорейтинговые комнаты"""
        return self.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(avg_rating__gte=min_rating)

    def with_all_amenities(self, amenity_names):
        """Получить комнаты со всеми указанными удобствами"""
        if not amenity_names:
            return self.none()
        query = Q()
        for amenity in amenity_names:
            query &= Q(amenities__name=amenity)
        return self.filter(query).distinct()

    def long_stay_rooms(self, days=7):
        """Получить комнаты с длительными бронированиями"""
        return self.annotate(
            max_stay=ExpressionWrapper(
                F('bookings__check_out') - F('bookings__check_in'),
                output_field=DurationField()
            )
        ).filter(max_stay__gte=timedelta(days=days)).distinct()

class BookingManager(models.Manager):
    def active_bookings(self):
        """Получить все активные бронирования"""
        today = timezone.now().date()
        return self.filter(
            status='confirmed',
            check_in__lte=today,
            check_out__gte=today
        )

    def upcoming_bookings(self):
        """Получить предстоящие бронирования"""
        return self.filter(
            status='confirmed',
            check_in__gt=timezone.now().date()
        ).order_by('check_in')

    def past_bookings(self):
        """Получить прошедшие бронирования"""
        return self.filter(
            check_out__lt=timezone.now().date()
        ).order_by('-check_out')

    def cancelled_bookings(self):
        """Получить отмененные бронирования"""
        return self.filter(status='cancelled')

    def get_guest_bookings(self, guest_id):
        """Получить все бронирования конкретного гостя"""
        return self.filter(guest_id=guest_id).order_by('-created_at')

    def get_long_stays(self, min_days=7):
        """Получить бронирования с длительным проживанием"""
        return self.annotate(
            stay_duration=ExpressionWrapper(
                F('check_out') - F('check_in'),
                output_field=DurationField()
            )
        ).filter(stay_duration__gte=timedelta(days=min_days))

    def get_recent_bookings(self, days=30):
        """Получить недавние бронирования"""
        recent_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=recent_date)

    def get_bookings_by_room_type(self, room_type):
        """Получить бронирования по типу комнаты"""
        return self.filter(room__room_type=room_type) 