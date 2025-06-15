# bookings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Room, Amenity, Booking, Review, SliderImage, SpecialOffer
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import ReviewForm
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .serializers import RoomSerializer, BookingSerializer, ReviewSerializer, UserSerializer, SliderImageSerializer, SpecialOfferSerializer
from django.db.models import Q
from datetime import datetime
from rest_framework.views import APIView

def index(request):
    rooms = Room.objects.all()
    return render(request, 'bookings/index.html', {'rooms': rooms})

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        # Обработка бронирования
        booking = Booking.objects.create(
            guest=request.user,
            room=room,
            check_in=request.POST['check_in'],
            check_out=request.POST['check_out'],
            guests_count=request.POST['guests_count']
        )
        messages.success(request, 'Бронирование успешно создано!')
        return HttpResponseRedirect(booking.get_absolute_url())
    return render(request, 'bookings/book_room.html', {'room': room})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, guest=request.user)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Бронирование успешно отменено!')
        return HttpResponseRedirect(reverse('booking-list'))
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})

@login_required
def modify_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, guest=request.user)
    if request.method == 'POST':
        # Обработка изменений
        booking.check_in = request.POST['check_in']
        booking.check_out = request.POST['check_out']
        booking.guests_count = request.POST['guests_count']
        booking.save()
        messages.success(request, 'Бронирование успешно изменено!')
        return HttpResponseRedirect(booking.get_absolute_url())
    return render(request, 'bookings/modify_booking.html', {'booking': booking})

@login_required
def add_review(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.guest = request.user
            review.room = room
            review.save()
            messages.success(request, 'Отзыв успешно добавлен!')
            return HttpResponseRedirect(room.get_reviews_url())
    else:
        form = ReviewForm()
    return render(request, 'bookings/add_review.html', {'form': form, 'room': room})

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, guest=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв успешно обновлен!')
            return HttpResponseRedirect(review.get_absolute_url())
    else:
        form = ReviewForm(instance=review)
    return render(request, 'bookings/edit_review.html', {'form': form, 'review': review})

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    context = {
        'room': room,
        'booking_url': room.get_booking_url(),
        'reviews_url': room.get_reviews_url(),
        'amenities_url': room.get_amenities_url(),
    }
    return render(request, 'bookings/room_detail.html', context)

def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    context = {
        'booking': booking,
        'cancel_url': booking.get_cancel_url(),
        'modify_url': booking.get_modify_url(),
        'payment_url': booking.get_payment_url(),
    }
    return render(request, 'bookings/booking_detail.html', context)

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    context = {
        'review': review,
        'edit_url': review.get_edit_url() if review.guest == request.user else None,
    }
    return render(request, 'bookings/review_detail.html', context)

def amenity_detail(request, pk):
    amenity = get_object_or_404(Amenity, pk=pk)
    context = {
        'amenity': amenity,
        'rooms_url': amenity.get_rooms_url(),
    }
    return render(request, 'bookings/amenity_detail.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Неверные логин или пароль')
    return redirect('index')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Пользователь с таким логином уже существует')
    return redirect('index')

def logout_view(request):
    logout(request)
    return redirect('index')
    
def index(request):
    rooms = Room.objects.all()
    return render(request, 'bookings/index.html', {'rooms': rooms})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'bookings/register.html', {'form': form})

def book_room(request, room_id):
    # Реализуйте вашу логику бронирования здесь
    return redirect('index')

@login_required
def add_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.guest = request.user
            review.review_date = timezone.now()
            review.save()
            return redirect('index')
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form})

@api_view(['GET'])
def available_rooms(request):
    """
    Получить список доступных комнат на указанные даты
    """
    check_in = request.query_params.get('check_in')
    check_out = request.query_params.get('check_out')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    exclude_amenity = request.query_params.get('exclude_amenity')

    try:
        # Преобразуем строки дат в объекты datetime
        if check_in and check_out:
            check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out, '%Y-%m-%d').date()
            rooms = Room.get_available_rooms(check_in, check_out)
        else:
            rooms = Room.objects.filter(is_available=True)

        # Применяем фильтр по цене
        if min_price or max_price:
            rooms = Room.get_rooms_by_price_range(
                min_price=float(min_price) if min_price else None,
                max_price=float(max_price) if max_price else None
            )

        # Исключаем комнаты с определенным удобством
        if exclude_amenity:
            rooms = rooms.exclude(amenities__name=exclude_amenity)

        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    except ValueError as e:
        return Response(
            {'error': 'Неверный формат данных'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def rooms_without_reviews(request):
    """
    Получить список комнат без отзывов
    """
    rooms = Room.get_rooms_without_reviews()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Получить доступные комнаты"""
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if check_in and check_out:
            try:
                check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out = datetime.strptime(check_out, '%Y-%m-%d').date()
                rooms = Room.rooms.available_rooms(check_in, check_out)
            except ValueError:
                return Response(
                    {'error': 'Неверный формат даты'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            rooms = Room.rooms.filter(is_available=True)
        
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def luxury(self, request):
        """Получить люкс-комнаты"""
        min_price = request.query_params.get('min_price', 5000)
        rooms = Room.rooms.luxury_rooms(float(min_price))
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def budget(self, request):
        """Получить бюджетные комнаты"""
        max_price = request.query_params.get('max_price', 2000)
        rooms = Room.rooms.budget_rooms(float(max_price))
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Получить популярные комнаты"""
        min_bookings = request.query_params.get('min_bookings', 5)
        rooms = Room.rooms.popular_rooms(int(min_bookings))
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Получить высокорейтинговые комнаты"""
        min_rating = request.query_params.get('min_rating', 4.0)
        rooms = Room.rooms.top_rated(float(min_rating))
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def with_amenities(self, request):
        """Получить комнаты с указанными удобствами"""
        amenities = request.query_params.getlist('amenities')
        if not amenities:
            return Response(
                {'error': 'Укажите хотя бы одно удобство'},
                status=status.HTTP_400_BAD_REQUEST
            )
        rooms = Room.rooms.with_all_amenities(amenities)
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def long_stays(self, request):
        """Получить комнаты с длительными бронированиями"""
        min_days = request.query_params.get('min_days', 7)
        rooms = Room.rooms.long_stay_rooms(int(min_days))
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """
        Получить отзывы о конкретной комнате
        """
        room = self.get_object()
        reviews = room.get_room_reviews()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def future_bookings(self, request, pk=None):
        """
        Получить будущие бронирования конкретной комнаты
        """
        room = self.get_object()
        bookings = room.get_future_bookings()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def high_rated(self, request):
        """
        Получить комнаты с высоким рейтингом
        """
        min_rating = request.query_params.get('min_rating', 4)
        rooms = Room.get_rooms_with_high_rated_reviews(min_rating=float(min_rating))
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent_bookings(self, request):
        """
        Получить комнаты с недавними бронированиями
        """
        days = request.query_params.get('days', 30)
        rooms = Room.get_rooms_with_recent_bookings(days=int(days))
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_guest_country(self, request):
        """
        Получить комнаты, забронированные гостями из определенной страны
        """
        country = request.query_params.get('country')
        if not country:
            return Response(
                {'error': 'Параметр country обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        rooms = Room.get_rooms_by_guest_country(country)
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_review_keyword(self, request):
        """
        Получить комнаты с отзывами, содержащими ключевое слово
        """
        keyword = request.query_params.get('keyword')
        if not keyword:
            return Response(
                {'error': 'Параметр keyword обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        rooms = Room.get_rooms_by_review_keywords(keyword)
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def guest_reviews(self, request, pk=None):
        """
        Получить отзывы конкретного гостя о комнате
        """
        room = self.get_object()
        guest_id = request.query_params.get('guest_id')
        if not guest_id:
            return Response(
                {'error': 'Параметр guest_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reviews = room.get_guest_reviews(guest_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def bookings_by_status(self, request, pk=None):
        """
        Получить бронирования комнаты с определенным статусом
        """
        room = self.get_object()
        status_param = request.query_params.get('status')
        if not status_param:
            return Response(
                {'error': 'Параметр status обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        bookings = room.get_bookings_by_status(status_param)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def future_bookings_with_guests(self, request, pk=None):
        """
        Получить будущие бронирования с информацией о гостях
        """
        room = self.get_object()
        bookings = room.get_future_bookings_with_guest_info()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить активные бронирования"""
        bookings = Booking.bookings.active_bookings()
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Получить предстоящие бронирования"""
        bookings = Booking.bookings.upcoming_bookings()
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Получить прошедшие бронирования"""
        bookings = Booking.bookings.past_bookings()
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cancelled(self, request):
        """Получить отмененные бронирования"""
        bookings = Booking.bookings.cancelled_bookings()
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def guest_bookings(self, request):
        """Получить бронирования конкретного гостя"""
        guest_id = request.query_params.get('guest_id')
        if not guest_id:
            return Response(
                {'error': 'Укажите ID гостя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        bookings = Booking.bookings.get_guest_bookings(guest_id)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def long_stays(self, request):
        """Получить бронирования с длительным проживанием"""
        min_days = request.query_params.get('min_days', 7)
        bookings = Booking.bookings.get_long_stays(int(min_days))
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Получить недавние бронирования"""
        days = request.query_params.get('days', 30)
        bookings = Booking.bookings.get_recent_bookings(int(days))
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_room_type(self, request):
        """Получить бронирования по типу комнаты"""
        room_type = request.query_params.get('room_type')
        if not room_type:
            return Response(
                {'error': 'Укажите тип комнаты'},
                status=status.HTTP_400_BAD_REQUEST
            )
        bookings = Booking.bookings.get_bookings_by_room_type(room_type)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-review_date')  # Сортировка по дате отзыва (сначала новые)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)

    def get_queryset(self):
        """
        Переопределяем queryset для добавления различных вариантов сортировки
        """
        queryset = super().get_queryset()
        sort_by = self.request.query_params.get('sort_by', None)
        
        if sort_by == 'rating':
            queryset = queryset.order_by('-rating', '-review_date')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('review_date')
            
        return queryset

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return Response({'detail': 'Successfully logged in.'})
    return Response({'detail': 'Invalid credentials.'}, status=400)

@api_view(['POST'])
def register_view(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if User.objects.filter(username=username).exists():
        return Response({'detail': 'Username already exists.'}, status=400)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)
    return Response({'detail': 'Successfully registered.'})

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'detail': 'Successfully logged out.'})

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Пользователь успешно зарегистрирован"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SliderImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SliderImage.objects.filter(is_active=True).order_by('order')
    serializer_class = SliderImageSerializer
    permission_classes = [AllowAny]

class SpecialOfferViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SpecialOffer.objects.filter(is_active=True)
    serializer_class = SpecialOfferSerializer
    permission_classes = [AllowAny]