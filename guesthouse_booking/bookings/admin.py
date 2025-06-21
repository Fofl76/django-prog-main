# bookings/admin.py

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path
from django.db import models
from .models import Guest, Room, Booking, Payment, Review, Amenity, SliderImage, SpecialOffer, UserRole, RoomSpecialOffer, Document
from .pdf_utils import (
    generate_room_statistics_pdf_unicode, 
    generate_room_statistics_html_pdf,
    generate_room_statistics_pdf_translit,
    generate_monthly_report_pdf, 
    generate_booking_report_pdf,
    generate_special_offers_report_pdf
)

# Модель-заглушка для дашборда
class Dashboard(models.Model):
    class Meta:
        verbose_name = 'Дашборд'
        verbose_name_plural = 'Дашборды'
        app_label = 'bookings'

    def __str__(self):
        return 'Дашборд гостиницы'

class AmenityInline(admin.TabularInline):
    """Инлайн для удобств в админке комнаты."""
    model = Room.amenities.through  

    def rooms_count(self, obj: Amenity) -> int:
        """Возвращает количество комнат для удобства."""
        try:
            return obj.rooms.count()
        except Exception:
            return 0

class RoomSpecialOfferInline(admin.TabularInline):
    model = RoomSpecialOffer
    extra = 1
    fields = ('special_offer', 'start_date', 'end_date', 'discount_percentage', 'is_active')

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'role', 'has_documents_display')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('role', 'first_name', 'last_name')
    raw_id_fields = ('user', 'role')
    
    # Поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone_number', 'role')
        }),
        ('Документы', {
            'fields': ('passport_scan', 'id_document', 'additional_documents'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Есть документы')
    def has_documents_display(self, obj):
        return bool(obj.passport_scan or obj.id_document or obj.additional_documents)
    has_documents_display.boolean = True

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'price_per_night', 'max_occupancy', 'has_active_offers_display', 'has_photo_display')
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number', 'room_type')
    inlines = [AmenityInline, RoomSpecialOfferInline]
    actions = ['generate_room_statistics_pdf', 'generate_monthly_report_pdf']
    
    # Поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('room_number', 'room_type', 'price_per_night', 'max_occupancy', 'is_available')
        }),
        ('Файлы', {
            'fields': ('photo', 'floor_plan', 'documents'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Активные предложения')
    def has_active_offers_display(self, obj):
        try:
            return obj.has_active_special_offers()
        except:
            return False
    has_active_offers_display.boolean = True

    @admin.display(description='Есть фото')
    def has_photo_display(self, obj):
        return bool(obj.photo)
    has_photo_display.boolean = True

    @admin.display(description='Удобства')
    def display_amenities(self, obj):
        try:
            return ", ".join([amenity.name for amenity in obj.amenities.all()])
        except:
            return ""

    def generate_room_statistics_pdf(self, request, queryset):
        """Генерирует PDF отчет со статистикой комнат"""
        try:
            # Пробуем разные методы генерации PDF
            try:
                # Сначала пробуем Unicode версию
                response = generate_room_statistics_pdf_unicode()
                messages.success(request, "PDF отчет со статистикой комнат успешно сгенерирован (Unicode)")
            except:
                try:
                    # Затем пробуем HTML версию
                    response = generate_room_statistics_html_pdf()
                    messages.success(request, "PDF отчет со статистикой комнат успешно сгенерирован (HTML)")
                except:
                    # В крайнем случае используем транслитерированную версию
                    response = generate_room_statistics_pdf_translit()
                    messages.success(request, "PDF отчет со статистикой комнат успешно сгенерирован (транслитерация)")
            
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
            return redirect('.')
    generate_room_statistics_pdf.short_description = "Сгенерировать PDF отчет со статистикой комнат"

    def generate_monthly_report_pdf(self, request, queryset):
        """Генерирует месячный PDF отчет"""
        try:
            current_date = timezone.now()
            response = generate_monthly_report_pdf(current_date.year, current_date.month)
            messages.success(request, f"Месячный PDF отчет за {current_date.strftime('%B %Y')} успешно сгенерирован")
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
            return redirect('.')
    generate_monthly_report_pdf.short_description = "Сгенерировать месячный PDF отчет"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('guest', 'room', 'check_in', 'check_out', 'total_price', 'status', 'has_documents_display')
    list_filter = ('status', 'check_in', 'check_out')
    date_hierarchy = 'check_in'
    raw_id_fields = ('guest', 'room')
    search_fields = ('guest__username', 'room__room_number')
    actions = ['generate_booking_report_pdf']
    
    # Поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('guest', 'room', 'check_in', 'check_out', 'guests_count', 'status')
        }),
        ('Документы', {
            'fields': ('contract', 'receipt', 'additional_files'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Есть документы')
    def has_documents_display(self, obj):
        return bool(obj.contract or obj.receipt or obj.additional_files)
    has_documents_display.boolean = True

    def generate_booking_report_pdf(self, request, queryset):
        """Генерирует PDF отчет по бронированиям"""
        try:
            response = generate_booking_report_pdf()
            messages.success(request, "PDF отчет по бронированиям успешно сгенерирован")
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
            return redirect('.')
    generate_booking_report_pdf.short_description = "Сгенерировать PDF отчет по бронированиям"

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_date', 'payment_method', 'status', 'has_documents_display')
    list_filter = ('payment_date', 'payment_method', 'status')
    date_hierarchy = 'payment_date'
    search_fields = ('booking__guest__first_name', 'booking__guest__last_name')
    
    # Поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('booking', 'amount', 'payment_date', 'payment_method', 'status')
        }),
        ('Документы', {
            'fields': ('payment_receipt', 'bank_statement', 'refund_document'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Есть документы')
    def has_documents_display(self, obj):
        return bool(obj.payment_receipt or obj.bank_statement or obj.refund_document)
    has_documents_display.boolean = True

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('room', 'guest', 'rating', 'review_date')
    list_filter = ('rating', 'review_date')
    search_fields = ('guest__first_name', 'guest__last_name', 'room__room_number')

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'rooms_count')
    search_fields = ('name',)

    @admin.display(description='Количество комнат')
    def rooms_count(self, obj: Amenity) -> int:
        """Возвращает количество комнат для удобства."""
        try:
            return obj.rooms.count()
        except Exception:
            return 0

@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('order', '-created_at')

@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_active', 'applications_count', 'active_applications_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'short_description', 'full_description')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['generate_special_offers_report_pdf']

    @admin.display(description='Всего применений')
    def applications_count(self, obj):
        try:
            return obj.get_total_applications_count()
        except:
            return 0

    @admin.display(description='Активных применений')
    def active_applications_count(self, obj):
        try:
            return obj.get_active_applications_count()
        except:
            return 0

    def generate_special_offers_report_pdf(self, request, queryset):
        """Генерирует PDF отчет по специальным предложениям"""
        try:
            response = generate_special_offers_report_pdf()
            messages.success(request, "PDF отчет по специальным предложениям успешно сгенерирован")
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
            return redirect('.')
    generate_special_offers_report_pdf.short_description = "Сгенерировать PDF отчет по специальным предложениям"

@admin.register(RoomSpecialOffer)
class RoomSpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('room', 'special_offer', 'start_date', 'end_date', 'discount_percentage', 'is_active', 'is_currently_active')
    list_filter = ('is_active', 'start_date', 'end_date', 'discount_percentage')
    search_fields = ('room__room_number', 'special_offer__title')
    date_hierarchy = 'start_date'
    raw_id_fields = ('room', 'special_offer')

    @admin.display(description='Активно сейчас')
    def is_currently_active(self, obj):
        try:
            return obj.is_currently_active()
        except:
            return False
    is_currently_active.boolean = True

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'uploaded_by', 'uploaded_at', 'is_public', 'file_size_display', 'related_object')
    list_filter = ('file_type', 'is_public', 'uploaded_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'uploaded_at'
    readonly_fields = ('uploaded_at', 'updated_at', 'file_size_display')
    
    # Поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'file', 'file_type', 'is_public')
        }),
        ('Связи', {
            'fields': ('room', 'guest', 'booking', 'payment'),
            'classes': ('collapse',)
        }),
        ('Метаданные', {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at', 'file_size_display'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Размер файла')
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    
    @admin.display(description='Связанный объект')
    def related_object(self, obj):
        if obj.room:
            return f"Комната: {obj.room.room_number}"
        elif obj.guest:
            return f"Гость: {obj.guest.first_name} {obj.guest.last_name}"
        elif obj.booking:
            return f"Бронирование: {obj.booking.id}"
        elif obj.payment:
            return f"Платёж: {obj.payment.id}"
        return "Не указан"

# Кастомная админка для дашборда с PDF отчетами
@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    change_list_template = 'admin/dashboard_change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-room-stats-pdf/', self.generate_room_stats_pdf, name='generate-room-stats-pdf'),
            path('generate-monthly-report-pdf/', self.generate_monthly_report_pdf, name='generate-monthly-report-pdf'),
            path('generate-booking-report-pdf/', self.generate_booking_report_pdf, name='generate-booking-report-pdf'),
            path('generate-special-offers-report-pdf/', self.generate_special_offers_report_pdf, name='generate-special-offers-report-pdf'),
        ]
        return custom_urls + urls

    def generate_room_stats_pdf(self, request):
        try:
            # Пробуем разные методы генерации PDF
            try:
                # Сначала пробуем Unicode версию
                response = generate_room_statistics_pdf_unicode()
                messages.success(request, "PDF отчет со статистикой комнат успешно сгенерирован (Unicode)")
            except:
                try:
                    # Затем пробуем HTML версию
                    response = generate_room_statistics_html_pdf()
                    messages.success(request, "PDF отчет со статистикой комнат успешно сгенерирован (HTML)")
                except:
                    # В крайнем случае используем транслитерированную версию
                    response = generate_room_statistics_pdf_translit()
                    messages.success(request, "PDF отчет со статистикой комнат успешно сгенерирован (транслитерация)")
            
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
            return redirect('admin:index')

    def generate_monthly_report_pdf(self, request):
        try:
            current_date = timezone.now()
            response = generate_monthly_report_pdf(current_date.year, current_date.month)
            messages.success(request, f"Месячный PDF отчет за {current_date.strftime('%B %Y')} успешно сгенерирован")
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
            return redirect('admin:index')

    def generate_booking_report_pdf(self, request):
        try:
            response = generate_booking_report_pdf()
            messages.success(request, "PDF отчет по бронированиям успешно сгенерирован")
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
            return redirect('admin:index')

    def generate_special_offers_report_pdf(self, request):
        try:
            response = generate_special_offers_report_pdf()
            messages.success(request, "PDF отчет по специальным предложениям успешно сгенерирован")
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")
            return redirect('admin:index')
