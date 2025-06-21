# guesthouse_booking/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from bookings.views import RoomViewSet, BookingViewSet, ReviewViewSet, SliderImageViewSet, SpecialOfferViewSet, RegisterView, ProfileViewSet, PaymentViewSet, AmenityViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'slider-images', SliderImageViewSet)
router.register(r'special-offers', SpecialOfferViewSet)
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'payments', PaymentViewSet)
router.register(r'amenities', AmenityViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    # path('silk/', include('silk.urls', namespace='silk')), # Temporarily removed for debugging
    path('__debug__/', include('debug_toolbar.urls')), # Added for diagnostics
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
