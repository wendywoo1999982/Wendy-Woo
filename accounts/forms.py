from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from .models import ProductReview


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")  # REMOVE username

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field completely
        if 'username' in self.fields:
            del self.fields['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        # Auto-generate username from email
        user.username = self.cleaned_data["email"]  # Set username = email
        user.is_active = False
        
        if commit:
            user.save()
        
        return user

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        verification_url = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        full_verification_url = f"http://127.0.0.1:8000{verification_url}"
        
        subject = 'Verify Your WENDY WOO Account'
        message = f'''
Hello {user.first_name},

Thank you for creating an account with WENDY WOO!

Please click the link below to verify your email address and activate your account:
{full_verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
WENDY WOO Team
        '''
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'utm2577239@stu.o-hara.ac.jp')
        send_mail(subject, message, from_email, [user.email], fail_silently=False)
        print(f"🔍 Email sent to: {user.email}")


# REVIEW FORM
class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment', 'photo']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Share your experience with this product...',
                'class': 'form-textarea'
            }),
        }
    
    rating = forms.IntegerField(
        widget=forms.RadioSelect(choices=[
            (1, '1 Star'),
            (2, '2 Stars'), 
            (3, '3 Stars'),
            (4, '4 Stars'),
            (5, '5 Stars')
        ])
    )

class EnquiryForm(forms.Form):
    INQUIRY_TYPES = [
        ('', 'Please select one'),
        ('orders', 'Orders'),
        ('product_ingredients', 'Product Ingredients'),
        ('others', 'Others'),
    ]
    
    inquiry_type = forms.ChoiceField(
        choices=INQUIRY_TYPES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'})
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'How can we help you?', 'rows': 5})
    )
    # ADD PHOTO FIELD
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-file-input',
            'accept': 'image/*'
        }),
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        help_text="Optional: Upload a photo related to your enquiry (max 5MB)"
    )
    
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Limit file size to 5MB
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 5MB )")
        return photo