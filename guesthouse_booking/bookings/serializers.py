from rest_framework import serializers
from .models import Room, Booking, Review, Amenity, SliderImage, SpecialOffer, Guest, Payment, UserRole
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from decimal import Decimal

class UserRoleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели UserRole."""
    class Meta:
        model = UserRole
        fields = ['id', 'name', 'description']

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class GuestSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Guest."""
    user = UserSerializer(read_only=True)
    role = UserRoleSerializer(read_only=True)
    total_bookings = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    last_booking = serializers.SerializerMethodField()

    class Meta:
        model = Guest
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email',
            'phone_number', 'role', 'created_at', 'updated_at',
            'total_bookings', 'total_spent', 'average_rating',
            'last_booking'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_bookings(self, obj):
        include_cancelled = self.context.get('include_cancelled', False)
        queryset = obj.user.bookings
        if not include_cancelled:
            queryset = queryset.exclude(status='cancelled')
        return queryset.count()

    def get_total_spent(self, obj):
        period = self.context.get('period', 'all')  # 'all', 'month', 'year'
        queryset = obj.user.bookings.all()
        
        if period == 'month':
            queryset = queryset.filter(created_at__month=timezone.now().month)
        elif period == 'year':
            queryset = queryset.filter(created_at__year=timezone.now().year)
            
        return sum(
            payment.amount
            for booking in queryset
            for payment in booking.payments.filter(status='completed')
        )

    def get_average_rating(self, obj):
        min_rating = self.context.get('min_rating', 0)
        reviews = Review.objects.filter(guest=obj.user, rating__gte=min_rating)
        if not reviews.exists():
            return 0
        return sum(review.rating for review in reviews) / reviews.count()

    def get_last_booking(self, obj):
        include_cancelled = self.context.get('include_cancelled', False)
        queryset = obj.user.bookings.order_by('-check_out')
        if not include_cancelled:
            queryset = queryset.exclude(status='cancelled')
            
        last_booking = queryset.first()
        if last_booking:
            return {
                'id': last_booking.id,
                'room_number': last_booking.room.room_number,
                'check_out': last_booking.check_out,
                'status': last_booking.status
            }
        return None

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        
        # Обновляем данные гостя
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

class AmenitySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Amenity."""
    rooms_count = serializers.SerializerMethodField()
    active_rooms_count = serializers.SerializerMethodField()

    class Meta:
        model = Amenity
        fields = ['id', 'name', 'rooms_count', 'active_rooms_count']

    def get_rooms_count(self, obj):
        return obj.rooms.count()

    def get_active_rooms_count(self, obj):
        return obj.rooms.filter(is_available=True).count()

class RoomSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Room."""
    amenities: AmenitySerializer = AmenitySerializer(many=True, read_only=True)
    average_rating: serializers.SerializerMethodField = serializers.SerializerMethodField()
    is_available_now: serializers.SerializerMethodField = serializers.SerializerMethodField()
    total_reviews: serializers.SerializerMethodField = serializers.SerializerMethodField()
    next_available_date: serializers.SerializerMethodField = serializers.SerializerMethodField()
    current_booking: serializers.SerializerMethodField = serializers.SerializerMethodField()
    price_with_discount: serializers.SerializerMethodField = serializers.SerializerMethodField()
    photo: serializers.ImageField = serializers.ImageField(read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'room_type', 'price_per_night',
            'max_occupancy', 'amenities', 'is_available',
            'average_rating', 'is_available_now', 'total_reviews',
            'next_available_date', 'current_booking', 'price_with_discount',
            'photo'
        ]

    def get_average_rating(self, obj: Room) -> float:
        """Возвращает средний рейтинг комнаты."""
        min_rating = self.context.get('min_rating', 0)
        reviews = obj.reviews.filter(rating__gte=min_rating)
        if not reviews.exists():
            return 0.0
        return sum(review.rating for review in reviews) / reviews.count()

    def get_is_available_now(self, obj):
        return obj.is_available

    def get_total_reviews(self, obj):
        min_rating = self.context.get('min_rating', 0)
        return obj.reviews.filter(rating__gte=min_rating).count()

    def get_next_available_date(self, obj):
        return None

    def get_current_booking(self, obj):
        booking = obj.get_current_booking()
        if booking:
            include_guest_details = self.context.get('include_guest_details', False)
            result = {
                'id': booking.id,
                'check_in': booking.check_in,
                'check_out': booking.check_out,
                'status': booking.status
            }
            if include_guest_details:
                result['guest_name'] = f"{booking.guest.first_name} {booking.guest.last_name}"
                result['guest_email'] = booking.guest.email
            return result
        return None

    def get_price_with_discount(self, obj):
        discount_percentage = self.context.get('discount_percentage', 0)
        if discount_percentage:
            return obj.price_per_night * (1 - discount_percentage / 100)
        return obj.price_per_night

class BookingSerializer(serializers.ModelSerializer):
    room_details = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    can_be_cancelled = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    guest_details = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'guest', 'room', 'check_in', 'check_out',
            'status', 'guests_count', 'created_at', 'room_details',
            'total_price', 'duration', 'can_be_cancelled', 'payment_status',
            'guest_details'
        ]
        read_only_fields = ['created_at']

    def get_room_details(self, obj):
        include_amenities = self.context.get('include_amenities', False)
        result = {
            'room_number': obj.room.room_number,
            'room_type': obj.room.room_type,
            'price_per_night': obj.room.price_per_night
        }
        if include_amenities:
            result['amenities'] = [amenity.name for amenity in obj.room.amenities.all()]
        return result

    def get_total_price(self, obj):
        include_discount = self.context.get('include_discount', False)
        discount_percentage = self.context.get('discount_percentage', 0)
        total = obj.total_price()
        if include_discount and discount_percentage:
            total *= (1 - discount_percentage / 100)
        return total

    def get_duration(self, obj):
        return (obj.check_out - obj.check_in).days

    def get_can_be_cancelled(self, obj):
        cancellation_policy = self.context.get('cancellation_policy', 'standard')
        return obj.can_be_cancelled(policy=cancellation_policy)

    def get_payment_status(self, obj):
        include_partial = self.context.get('include_partial', True)
        payments = obj.payments.all()
        if not payments.exists():
            return 'unpaid'
        total_paid = sum(payment.amount for payment in payments if payment.status == 'completed')
        if total_paid >= obj.total_price():
            return 'paid'
        return 'partially_paid' if include_partial else 'unpaid'

    def get_guest_details(self, obj):
        include_contact = self.context.get('include_contact', False)
        result = {
            'name': f"{obj.guest.first_name} {obj.guest.last_name}",
            'id': obj.guest.id
        }
        if include_contact:
            result['email'] = obj.guest.email
            result['phone'] = obj.guest.phone_number
        return result

class ReviewSerializer(serializers.ModelSerializer):
    guest_name = serializers.SerializerMethodField()
    room_details = serializers.SerializerMethodField()
    review_age = serializers.SerializerMethodField()
    formatted_comment = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'room', 'guest', 'rating', 'comment',
            'review_date', 'guest_name', 'room_details',
            'review_age', 'formatted_comment', 'formatted_date'
        ]
        read_only_fields = ['review_date']

    def get_guest_name(self, obj):
        if not obj.guest:
            return "Аноним"
        
        include_title = self.context.get('include_title', False)
        name = f"{obj.guest.first_name} {obj.guest.last_name}".strip()
        
        if not name:
            name = obj.guest.username

        if include_title and hasattr(obj.guest, 'guest_profile') and obj.guest.guest_profile.role:
            name = f"{obj.guest.guest_profile.role.name} {name}"
        return name

    def get_room_details(self, obj):
        include_price = self.context.get('include_price', False)
        result = {
            'room_number': obj.room.room_number,
            'room_type': obj.room.room_type
        }
        if include_price:
            result['price_per_night'] = obj.room.price_per_night
        return result

    def get_review_age(self, obj):
        return (timezone.now().date() - obj.review_date.date()).days

    def get_formatted_comment(self, obj):
        max_length = self.context.get('max_comment_length', None)
        if max_length and len(obj.comment) > max_length:
            return obj.comment[:max_length] + '...'
        return obj.comment

    def get_formatted_date(self, obj):
        return obj.review_date.strftime('%d.%m.%Y')

class SliderImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    display_duration = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = SliderImage
        fields = ['id', 'image', 'title', 'description', 'order', 'is_active', 'image_url', 'display_duration', 'thumbnail_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        size = self.context.get('image_size', 'original')
        if request and obj.image:
            if size == 'thumbnail':
                return request.build_absolute_uri(obj.image.url.replace('/original/', '/thumbnail/'))
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_display_duration(self, obj):
        return self.context.get('default_duration', 5000)

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url.replace('/original/', '/thumbnail/'))
        return None

class SpecialOfferSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOffer
        fields = [
            'id', 'title', 'image', 'image_url', 'short_description',
            'full_description', 'price', 'is_active',
            'created_at', 'updated_at', 'discount_percentage',
            'days_remaining', 'final_price'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return ""

    def get_discount_percentage(self, obj):
        base_discount = self.context.get('base_discount', 15)
        avg_discount = obj.room_special_offers.aggregate(avg=Avg('discount_percentage'))['avg']
        return avg_discount or base_discount

    def get_days_remaining(self, obj):
        max_days = self.context.get('max_days', 30)
        days = (obj.created_at + timedelta(days=max_days) - timezone.now()).days
        return max(0, days)

    def get_is_active(self, obj):
        max_days = self.context.get('max_days', 30)
        return obj.is_active and (timezone.now() - obj.created_at).days < max_days

    def get_final_price(self, obj):
        if obj.price is None:
            return None

        include_tax = self.context.get('include_tax', False)
        tax_rate = self.context.get('tax_rate', 0.2)
        
        discount_percentage = self.get_discount_percentage(obj)
        if not isinstance(discount_percentage, Decimal):
            discount_percentage = Decimal(str(discount_percentage))

        price = obj.price * (Decimal('1') - discount_percentage / Decimal('100'))

        if include_tax:
            if not isinstance(tax_rate, Decimal):
                tax_rate = Decimal(str(tax_rate))
            price *= (Decimal('1') + tax_rate)
        return price

class PaymentSerializer(serializers.ModelSerializer):
    booking_details = serializers.SerializerMethodField()
    payment_age = serializers.SerializerMethodField()
    is_refundable = serializers.SerializerMethodField()
    formatted_amount = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'payment_date',
            'payment_method', 'status', 'booking_details',
            'payment_age', 'is_refundable', 'formatted_amount'
        ]
        read_only_fields = ['id', 'payment_date']

    def get_booking_details(self, obj):
        include_room_details = self.context.get('include_room_details', False)
        result = {
            'room_number': obj.booking.room.room_number,
            'check_in': obj.booking.check_in,
            'check_out': obj.booking.check_out,
            'guest_name': f"{obj.booking.guest.first_name} {obj.booking.guest.last_name}"
        }
        if include_room_details:
            result['room_type'] = obj.booking.room.room_type
            result['price_per_night'] = obj.booking.room.price_per_night
        return result

    def get_payment_age(self, obj):
        return (timezone.now().date() - obj.payment_date).days

    def get_is_refundable(self, obj):
        refund_period = self.context.get('refund_period', 30)
        return obj.status == 'completed' and self.get_payment_age(obj) < refund_period

    def get_formatted_amount(self, obj):
        currency = self.context.get('currency', 'RUB')
        include_tax = self.context.get('include_tax', False)
        tax_rate = self.context.get('tax_rate', 0.2)
        
        amount = obj.amount
        if include_tax:
            amount *= (1 + tax_rate)
            
        return f"{amount:.2f} {currency}" 