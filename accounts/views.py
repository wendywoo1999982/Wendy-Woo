from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from .forms import SignUpForm, ReviewForm, EnquiryForm
from .models import Category, Product, ProductReview


# ===== AUTHENTICATION VIEWS =====
class SignInView(LoginView):
    template_name = 'login.html'
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(self.request, user)
                return redirect(self.get_success_url())
            else:
                messages.error(
                    self.request,
                    'Your account is not active. Please check your email for the verification link.'
                )
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('main')
    
    def form_valid(self, form):
        print("🔍 DEBUG 1: Starting signup process")
        
        # Create user but don't activate yet
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        print(f"🔍 DEBUG 2: User created - {user.username}, {user.email}")
        
        # Send verification email
        try:
            print("🔍 DEBUG 3: Starting email process")
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            print(f"🔍 DEBUG 4: Token and UID generated")
            
            verification_url = self.request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            print(f"🔍 DEBUG 5: Verification URL created: {verification_url}")
            
            subject = 'Verify Your WENDY WOO Account'
            message = f'''
Hello {user.first_name},

Thank you for creating an account with WENDY WOO!

Please click the link below to verify your email address and activate your account:
{verification_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
WENDY WOO Team
            '''
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'utm2577239@stu.o-hara.ac.jp')
            print(f"🔍 DEBUG 6: From email: {from_email}, To: {user.email}")
            
            print("🔍 DEBUG 7: About to call send_mail")
            send_mail(
                subject,
                message,
                from_email,
                [user.email],
                fail_silently=False,
            )
            print("🔍 DEBUG 8: send_mail completed successfully!")
            
        except Exception as e:
            print(f"🔍 DEBUG ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        messages.success(
            self.request,
            f'Welcome {user.first_name}! Please check your email to verify your account.'
        )
        print("🔍 DEBUG 9: Success message set, redirecting to main")
        return redirect('main')


def verify_email(request, uidb64, token):
    """
    Verify user's email address and activate account
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        messages.success(request, 'Your email has been verified! Your account is now active.')
        return redirect('main')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('login')


def custom_logout(request):
    """
    Custom logout view that redirects immediately to main page
    """
    logout(request)
    return redirect('main')


# ===== PASSWORD RESET VIEWS =====
def forgot_password(request):
    """
    Handle password reset requests
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(
                reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            subject = 'Password Reset Request - WENDY WOO'
            message = f'''
Hello {user.first_name or user.username},

You requested a password reset for your WENDY WOO account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
WENDY WOO Team
            '''
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'utm2577239@stu.o-hara.ac.jp')
            
            send_mail(
                subject,
                message,
                from_email,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, f'Password reset email has been sent to {email}')
            return redirect('forgot_password')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address')
    
    return render(request, 'forgot_password.html')


def test_smtp(request):
    try:
        send_mail(
            'SMTP Test - WENDY WOO',
            'This is a test email from your Django application.',
            settings.DEFAULT_FROM_EMAIL,
            ['your-test-email@gmail.com'],  # Change to your email
            fail_silently=False,
        )
        return JsonResponse({"status": "Email sent successfully!"})
    except Exception as e:
        return JsonResponse({"error": str(e)})


# ===== PROFILE & ACCOUNT VIEWS =====
@login_required
def profile(request):
    """
    User profile page after login - shows specific user data
    """
    return render(request, 'profile.html', {'user': request.user})


@login_required
def order_history(request):
    """
    User's order history page
    """
    orders = []  # You can populate this with actual orders when you have an Order model
    return render(request, 'orders.html', {
        'user': request.user,
        'orders': orders
    })


@login_required
def settings(request):
    """
    User settings page (mainly for password change)
    """
    return render(request, 'settings.html', {'user': request.user})


# ===== CART VIEWS =====
# @require_POST  # ← Remove or comment out this line
def add_to_cart(request, product_id):
    """
    Add product to cart and update session
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Initialize cart in session
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    cart = request.session['cart']
    
    # Add product to cart
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    
    # Save to session
    request.session['cart'] = cart
    request.session.modified = True
    
    # Update cart summary
    update_cart_summary(request)
    
    messages.success(request, f"Added {product.name} to cart!")
    return redirect('shopnow')


def update_cart_summary(request):
    """Update cart count and total"""
    cart = request.session.get('cart', {})
    
    total_items = 0
    total_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            total_items += quantity
            total_price += product.price * quantity
        except (Product.DoesNotExist, ValueError):
            continue
    
    request.session['cart_count'] = total_items
    request.session['cart_total'] = total_price
    request.session.modified = True


# ===== CONTEXT PROCESSOR FOR CART DATA =====
def cart_context(request):
    """
    Make cart data available in all templates
    """
    cart_count = request.session.get('cart_count', 0)
    cart_total = request.session.get('cart_total', 0)
    cart = request.session.get('cart', {})
    
    # Get actual product details for the cart popup
    cart_items = []
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': product.price * quantity
            })
        except (Product.DoesNotExist, ValueError):
            continue
    
    return {
        'cart_items_count': cart_count,
        'cart_total': cart_total,
        'cart_items': cart_items,
    }


# ===== ENQUIRIES VIEWS =====
def enquiries(request):
    """
    Handle customer enquiries and send emails with photo attachment
    """
    INQUIRY_TYPES = [
        ('', 'Please select one'),
        ('orders', 'Orders'),
        ('product_ingredients', 'Product Ingredients'),
        ('others', 'Others'),
    ]
    
    print("🟢 DEBUG: Enquiries view called")
    
    if request.method == 'POST':
        print("🟢 DEBUG: POST request received")
        form = EnquiryForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("🟢 DEBUG: Form is valid")
            # Get form data
            inquiry_type = form.cleaned_data['inquiry_type']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            photo = form.cleaned_data.get('photo')
            
            print(f"🟢 DEBUG: Photo received: {bool(photo)}")
            if photo:
                print(f"🟢 DEBUG: Photo details - Name: {photo.name}, Size: {photo.size} bytes")
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'utm2577239@stu.o-hara.ac.jp')
            inquiry_type_display = dict(INQUIRY_TYPES).get(inquiry_type, inquiry_type)
            
            try:
                # Send confirmation email to user
                send_mail(
                    subject="Thank you for your enquiry - WENDY WOO",
                    message=f"""Dear {name},

Thank you for contacting WENDY WOO. We have received your enquiry regarding {inquiry_type_display}.

We will get back to you within 24-48 hours.

Your message:
{message}

Best regards,
WENDY WOO Team""",
                    from_email=from_email,
                    recipient_list=[email],
                    fail_silently=False,
                )
                print("✅ DEBUG: User email sent")
                
                # Send email to admin with photo attachment
                admin_subject = f"📷 ENQUIRY WITH PHOTO - {inquiry_type_display}" if photo else f"Enquiry - {inquiry_type_display}"
                
                admin_email = EmailMessage(
                    subject=admin_subject,
                    body=f"""
NEW ENQUIRY RECEIVED

Inquiry Type: {inquiry_type_display}
Name: {name}
Email: {email}
Photo Attached: {'YES 📸' if photo else 'No'}

Message:
{message}

---
Sent from WENDY WOO Contact Form
""",
                    from_email=from_email,
                    to=[from_email],
                )
                
                # Attach photo if available
                if photo:
                    try:
                        photo_content = photo.read()
                        admin_email.attach(photo.name, photo_content, photo.content_type)
                        print("✅ DEBUG: Photo attached to admin email")
                    except Exception as e:
                        print(f"🔴 DEBUG: Photo attachment error: {e}")
                
                admin_email.send(fail_silently=False)
                print("✅ DEBUG: Admin email sent with photo attachment")
                
                # REDIRECT TO SUCCESS PAGE
                return redirect('enquiry_success')
                
            except Exception as e:
                print(f"🔴 DEBUG: Email error: {e}")
                messages.error(request, '❌ There was an error sending your enquiry. Please try again.')
        else:
            print(f"🔴 DEBUG: Form errors: {form.errors}")
            messages.error(request, '❌ Please correct the errors below.')
    
    else:
        form = EnquiryForm()
    
    return render(request, 'enquiries.html', {'form': form})

def enquiry_success(request):
    """
    Show success page after enquiry submission
    """
    return render(request, 'enquiry_success.html')

# ===== PAGE VIEWS =====
def main_page(request):
    """
    Main informative homepage
    """
    return render(request, 'main.html')


def menu_page(request):
    """
    Menu page
    """
    return render(request, 'menu.html')


def shopnow(request):
    """
    Shop now page with products
    """
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    return render(request, 'shopnow.html', {
        'categories': categories,
        'products': products
    })


# ===== PRODUCT REVIEW VIEWS =====
def product_detail(request, product_id):
    """
    Product detail page with reviews
    """
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    
    context = {
        'product': product,
        'reviews': reviews,
        'review_form': ReviewForm(),
    }
    return render(request, 'product_detail.html', context)


@login_required
def add_review(request, product_id):
    """
    Add a review for a product
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user already reviewed this product
    existing_review = ProductReview.objects.filter(product=product, user=request.user).first()
    if existing_review:
        messages.warning(request, 'You have already reviewed this product.')
        return redirect('product_detail', product_id=product.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            messages.success(request, 'Thank you for your review!')
            return redirect('product_detail', product_id=product.id)
        else:
            messages.error(request, 'Please check your review details.')
    
    return redirect('product_detail', product_id=product.id)


# ===== SEARCH VIEWS =====
def search_results(request):
    query = request.GET.get('q', '')
    return render(request, 'search_results.html', {
        'query': query,
        'products': []
    })


def search_ajax(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )[:5]  # Limit to 5 results for dropdown
        
        results = [
            {
                'id': product.id,
                'name': product.name,
                'price': f"¥{product.price}",
                'url': product.get_absolute_url()
            }
            for product in products
        ]
    
    return JsonResponse({'results': results})

# Add this temporary debug view to your views.py
def debug_cart(request):
    """
    Debug view to check cart session data
    """
    cart = request.session.get('cart', {})
    cart_count = request.session.get('cart_count', 0)
    cart_total = request.session.get('cart_total', 0)
    
    print("🛒 DEBUG CART SESSION:")
    print(f"Cart items: {cart}")
    print(f"Cart count: {cart_count}")
    print(f"Cart total: {cart_total}")
    
    # Check if products exist
    from .models import Product
    for product_id in cart.keys():
        try:
            product = Product.objects.get(id=int(product_id))
            print(f"✅ Product {product_id}: {product.name} - exists")
        except Product.DoesNotExist:
            print(f"❌ Product {product_id}: DOES NOT EXIST")
    
    return redirect('shopnow')