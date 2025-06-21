import django_filters
from .models import Room, Booking, Review, Payment, Guest

class RoomFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price_per_night", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price_per_night", lookup_expr='lte')
    room_type = django_filters.CharFilter(field_name="room_type", lookup_expr='icontains')
    min_occupancy = django_filters.NumberFilter(field_name="max_occupancy", lookup_expr='gte')
    amenities = django_filters.CharFilter(field_name="amenities__name", lookup_expr='icontains')
    is_available = django_filters.BooleanFilter(field_name="is_available")

    class Meta:
        model = Room
        fields = ['room_type', 'is_available', 'amenities']

class BookingFilter(django_filters.FilterSet):
    check_in_after = django_filters.DateFilter(field_name="check_in", lookup_expr='gte')
    check_in_before = django_filters.DateFilter(field_name="check_in", lookup_expr='lte')
    check_out_after = django_filters.DateFilter(field_name="check_out", lookup_expr='gte')
    check_out_before = django_filters.DateFilter(field_name="check_out", lookup_expr='lte')
    status = django_filters.CharFilter(field_name="status")
    room_type = django_filters.CharFilter(field_name="room__room_type", lookup_expr='icontains')
    min_guests = django_filters.NumberFilter(field_name="guests_count", lookup_expr='gte')

    class Meta:
        model = Booking
        fields = ['status', 'room', 'guest']

class ReviewFilter(django_filters.FilterSet):
    min_rating = django_filters.NumberFilter(field_name="rating", lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name="rating", lookup_expr='lte')
    room_type = django_filters.CharFilter(field_name="room__room_type", lookup_expr='icontains')
    review_date_after = django_filters.DateFilter(field_name="review_date", lookup_expr='gte')
    review_date_before = django_filters.DateFilter(field_name="review_date", lookup_expr='lte')

    class Meta:
        model = Review
        fields = ['room', 'guest', 'rating']

class PaymentFilter(django_filters.FilterSet):
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='lte')
    payment_date_after = django_filters.DateFilter(field_name="payment_date", lookup_expr='gte')
    payment_date_before = django_filters.DateFilter(field_name="payment_date", lookup_expr='lte')
    payment_method = django_filters.CharFilter(field_name="payment_method")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = Payment
        fields = ['payment_method', 'status', 'booking']

class GuestFilter(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name="role__name", lookup_expr='icontains')
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr='lte')
    email = django_filters.CharFilter(field_name="email", lookup_expr='icontains')
    phone = django_filters.CharFilter(field_name="phone_number", lookup_expr='icontains')

    class Meta:
        model = Guest
        fields = ['role', 'email', 'phone_number'] 