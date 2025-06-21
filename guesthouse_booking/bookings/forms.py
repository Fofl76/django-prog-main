from django import forms
from .models import Review
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Guest, Room, Booking, Payment, Document

class GuestRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    
    # Поля для файлов
    passport_scan = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Скан или фото паспорта (PDF, JPG, PNG)'
    )
    id_document = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Удостоверение личности (PDF, JPG, PNG)'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class RoomForm(forms.ModelForm):
    # Поля для файлов
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Фото комнаты (JPG, PNG, GIF)'
    )
    floor_plan = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='План этажа (PDF, JPG, PNG)'
    )
    documents = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Дополнительные документы (PDF, DOC, DOCX)'
    )
    
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price_per_night', 'max_occupancy', 'is_available', 'photo', 'floor_plan', 'documents']

class BookingForm(forms.ModelForm):
    # Поля для файлов
    contract = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Договор бронирования (PDF)'
    )
    receipt = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Квитанция об оплате (PDF, JPG, PNG)'
    )
    
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests_count', 'contract', 'receipt']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guests_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

class PaymentForm(forms.ModelForm):
    # Поля для файлов
    payment_receipt = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Квитанция об оплате (PDF, JPG, PNG)'
    )
    bank_statement = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Банковская выписка (PDF)'
    )
    
    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'payment_method', 'payment_receipt', 'bank_statement']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'file_type', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DocumentFilterForm(forms.Form):
    file_type = forms.ChoiceField(
        choices=[('', 'Все типы')] + Document.DOCUMENT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_public = forms.ChoiceField(
        choices=[('', 'Все'), ('True', 'Публичные'), ('False', 'Приватные')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    uploaded_after = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    uploaded_before = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по названию...'})
    )

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class BulkDocumentUploadForm(forms.Form):
    files = MultipleFileField(
        help_text='Выберите несколько файлов для загрузки',
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}),
    )
    file_type = forms.ChoiceField(
        choices=Document.DOCUMENT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_public = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    description_template = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Шаблон описания (используйте {filename} для имени файла)'
    )

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['room', 'rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите email'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'password')
