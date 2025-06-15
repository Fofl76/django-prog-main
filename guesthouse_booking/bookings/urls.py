from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from . import views

router = DefaultRouter()
router.register(r'rooms', views.RoomViewSet)
router.register(r'bookings', views.BookingViewSet)
router.register(r'reviews', views.ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Статистика и аналитика
    path('rooms/statistics/', views.RoomViewSet.as_view({'get': 'statistics'}), name='room-statistics'),
    path('rooms/room-types-analysis/', views.RoomViewSet.as_view({'get': 'room_types_analysis'}), name='room-types-analysis'),
    path('rooms/monthly-stats/', views.RoomViewSet.as_view({'get': 'monthly_stats'}), name='monthly-stats'),
    
    # Детальные страницы
    path('rooms/<int:pk>/', views.room_detail, name='room-detail'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking-detail'),
    path('reviews/<int:pk>/', views.review_detail, name='review-detail'),
    path('amenities/<int:pk>/', views.amenity_detail, name='amenity-detail'),
    
    # URLs для комнат
    path('rooms/<int:pk>/reviews/', views.RoomViewSet.as_view({'get': 'reviews'}), name='room-reviews'),
    path('rooms/<int:pk>/amenities/', views.RoomViewSet.as_view({'get': 'amenities'}), name='room-amenities'),
    path('rooms/<int:room_id>/book/', views.book_room, name='book_room'),
    path('rooms/<int:room_id>/add_review/', views.add_review, name='add-review'),
    
    # URLs для бронирований
    path('bookings/', views.BookingViewSet.as_view({'get': 'list'}), name='booking-list'),
    path('bookings/<int:pk>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('bookings/<int:pk>/modify/', views.modify_booking, name='modify-booking'),
    path('bookings/<int:pk>/payment/', views.BookingViewSet.as_view({'get': 'payment'}), name='booking-payment'),
    
    # URLs для отзывов
    path('reviews/<int:pk>/edit/', views.edit_review, name='edit-review'),
    
    # URLs для удобств
    path('amenities/<int:pk>/rooms/', views.RoomViewSet.as_view({'get': 'by_amenity'}), name='amenity-rooms'),
    
    # URLs для фильтрации комнат
    path('rooms/available/', views.RoomViewSet.as_view({'get': 'available'}), name='available-rooms'),
    path('rooms/luxury/', views.RoomViewSet.as_view({'get': 'luxury'}), name='luxury-rooms'),
    path('rooms/budget/', views.RoomViewSet.as_view({'get': 'budget'}), name='budget-rooms'),
    path('rooms/popular/', views.RoomViewSet.as_view({'get': 'popular'}), name='popular-rooms'),
    path('rooms/top-rated/', views.RoomViewSet.as_view({'get': 'top_rated'}), name='top-rated-rooms'),
    
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='bookings/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
]
