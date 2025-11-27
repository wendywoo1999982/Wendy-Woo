# ===== DJANGO IMPORTS =====
from django.contrib.auth.views import LoginView, PasswordResetConfirmView, PasswordResetCompleteView
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
import json
from .models import Category, Product

# ===== LOCAL IMPORTS =====
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
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        
        # Send verification email
        try:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            verification_url = self.request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )
            
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
            
            send_mail(
                subject,
                message,
                from_email,
                [user.email],
                fail_silently=False,
            )
            
        except Exception as e:
            print(f"Email error: {e}")
        
        messages.success(
            self.request,
            f'Welcome {user.first_name}! Please check your email to verify your account.'
        )
        return redirect('main')


def verify_email(request, uidb64, token):
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
    logout(request)
    return redirect('main')


# ===== PASSWORD RESET =====
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
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


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


# ===== PROFILE VIEWS =====
@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required
def order_history(request):
    orders = []
    return render(request, 'orders.html', {
        'user': request.user,
        'orders': orders
    })


@login_required
def settings(request):
    return render(request, 'settings.html', {'user': request.user})


# ===== CART VIEWS =====
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    update_cart_summary(request)
    messages.success(request, f"Added {product.name} to cart!")
    return redirect('shopnow')


def update_cart_summary(request):
    cart = request.session.get('cart', {})
    total_items = 0
    total_price = 0
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=int(pid))
            total_items += qty
            total_price += product.price * qty
        except Product.DoesNotExist:
            continue
    request.session['cart_count'] = total_items
    request.session['cart_total'] = total_price
    request.session.modified = True


# ===== CART API VIEWS =====
def get_cart_data(request):
    try:
        cart = request.session.get('cart', {})
        
        total_items = 0
        total_price = 0
        cart_items = []
        
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                item_total = product.price * quantity
                total_items += quantity
                total_price += item_total
                
                cart_items.append({
                    'id': product_id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                    'total_price': float(item_total)
                })
            except (Product.DoesNotExist, ValueError):
                continue
        
        return JsonResponse({
            'success': True,
            'total_items': total_items,
            'total_price': float(total_price),
            'items': cart_items
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = str(data.get('item_id'))
        quantity = int(data.get('quantity', 1))
        
        cart = request.session.get('cart', {})
        
        if item_id in cart:
            if quantity > 0:
                cart[item_id] = quantity
            else:
                del cart[item_id]
        else:
            cart[item_id] = quantity
        
        request.session['cart'] = cart
        request.session.modified = True
        
        update_cart_summary(request)
        
        return JsonResponse({
            'success': True,
            'total_items': request.session.get('cart_count', 0),
            'total_price': float(request.session.get('cart_total', 0))
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def remove_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = str(data.get('item_id'))
        
        cart = request.session.get('cart', {})
        
        if item_id in cart:
            del cart[item_id]
            request.session['cart'] = cart
            request.session.modified = True
            
            update_cart_summary(request)
            
            return JsonResponse({
                'success': True,
                'total_items': request.session.get('cart_count', 0),
                'total_price': float(request.session.get('cart_total', 0))
            })
        else:
            return JsonResponse({'success': False, 'error': 'Item not found in cart'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ===== CONTEXT PROCESSOR =====
def cart_context(request):
    cart_count = request.session.get('cart_count', 0)
    cart_total = request.session.get('cart_total', 0)
    cart = request.session.get('cart', {})
    
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


# ===== CHECKOUT VIEWS =====
# ===== CHECKOUT VIEWS =====
def checkout(request):
    """Main checkout page - redirects to appropriate step"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('/accounts/login/?next=/checkout/')
    
    # Check if cart is empty
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_page')
    
    # Redirect to payment page (since we only have COD)
    return redirect('payment_page')


def check_auth(request):
    """Check if user is authenticated"""
    return JsonResponse({
        'authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None
    })


@login_required
def payment_page(request):
    """Payment confirmation page for authenticated users"""
    cart = request.session.get('cart', {})
    
    total_items = 0
    total_price = 0
    cart_items = []
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = product.price * quantity
            total_items += quantity
            total_price += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total
            })
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
    }
    
    return render(request, 'checkout/payment.html', context)


def cart_page(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_items = 0
    total_price = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
            total_items += quantity
            total_price += item_total
        except Product.DoesNotExist:
            continue

    return render(request, 'cart_page.html', {
        'cart_items': cart_items,
        'cart_items_count': total_items,
        'cart_total': total_price,
    })

# ===== PAGE VIEWS =====
def main_page(request):
    return render(request, 'main.html')


def menu_page(request):
    return render(request, 'menu.html')


def shopnow(request):
    categories = Category.objects.prefetch_related('product_set').all()
    return render(request, 'shopnow.html', {
        'categories': categories
    })


def location(request):
    return render(request, 'location.html')


# ===== PRODUCT VIEWS =====
def product_detail(request, product_id):
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
    product = get_object_or_404(Product, id=product_id)
    
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
        )[:5]
        
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


# ===== ENQUIRIES =====
def enquiries(request):
    INQUIRY_TYPES = [
        ('', 'Please select one'),
        ('orders', 'Orders'),
        ('product_ingredients', 'Product Ingredients'),
        ('others', 'Others'),
    ]
    
    if request.method == 'POST':
        form = EnquiryForm(request.POST, request.FILES)
        
        if form.is_valid():
            inquiry_type = form.cleaned_data['inquiry_type']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            photo = form.cleaned_data.get('photo')
            
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
                
                # Send email to admin with photo attachment
                admin_subject = f"ENQUIRY WITH PHOTO - {inquiry_type_display}" if photo else f"Enquiry - {inquiry_type_display}"
                
                admin_email = EmailMessage(
                    subject=admin_subject,
                    body=f"""
NEW ENQUIRY RECEIVED

Inquiry Type: {inquiry_type_display}
Name: {name}
Email: {email}
Photo Attached: {'YES' if photo else 'No'}

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
                    except Exception as e:
                        print(f"Photo attachment error: {e}")
                
                admin_email.send(fail_silently=False)
                
                return redirect('enquiry_success')
                
            except Exception as e:
                messages.error(request, 'There was an error sending your enquiry. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    else:
        form = EnquiryForm()
    
    return render(request, 'enquiries.html', {'form': form})


def enquiry_success(request):
    return render(request, 'enquiry_success.html')


# ===== DEBUG/UTILITY =====
def debug_cart(request):
    cart = request.session.get('cart', {})
    cart_count = request.session.get('cart_count', 0)
    cart_total = request.session.get('cart_total', 0)
    
    print("DEBUG CART SESSION:")
    print(f"Cart items: {cart}")
    print(f"Cart count: {cart_count}")
    print(f"Cart total: {cart_total}")
    
    for product_id in cart.keys():
        try:
            product = Product.objects.get(id=int(product_id))
            print(f"Product {product_id}: {product.name} - exists")
        except Product.DoesNotExist:
            print(f"Product {product_id}: DOES NOT EXIST")
    
    return redirect('shopnow')