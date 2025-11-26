from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Import all views

urlpatterns = [
    path('', views.main_page, name='main'),
    path('menu/', views.menu_page, name='menu'),
    path('shopnow/', views.shopnow, name='shopnow'),  # Temporarily disabled
    path('login/', views.SignInView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', views.custom_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('profile/', views.profile, name='profile'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # path('orders/', views.order_history, name='order_history'),  # COMMENT THIS OUT FOR NOW
    # path('settings/', views.settings, name='settings'),  # COMMENT THIS OUT FOR NOW
    
    # PRODUCT URLs - REMOVED DUPLICATE
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/add-review/', views.add_review, name='add_review'),
    
    # ENQUIRY URLs
    path('enquiries/', views.enquiries, name='enquiries'),
    path('enquiry-success/', views.enquiry_success, name='enquiry_success'),
    
    # SEARCH URLs - THESE ARE CRITICAL
    path('search/', views.search_results, name='search_results'),
    path('api/search/', views.search_ajax, name='search_ajax'),  # This is the API endpoint
    
    # PASSWORD RESET
    path('password-reset/', 
     auth_views.PasswordResetView.as_view(
         template_name='password_reset.html',
         email_template_name='password_reset_email.html',
         subject_template_name='password_reset_subject.txt'
     ), 
     name='password_reset'),
    
path('password-reset/done/', 
     auth_views.PasswordResetDoneView.as_view(
         template_name='password_reset_done.html'
     ), 
     name='password_reset_done'),
    
# FIX: Use the expected URL pattern
path('reset/<uidb64>/<token>/', 
     auth_views.PasswordResetConfirmView.as_view(
         template_name='password_reset_confirm.html'
     ), 
     name='password_reset_confirm'),
    
path('password-reset-complete/', 
     auth_views.PasswordResetCompleteView.as_view(
         template_name='password_reset_complete.html'
     ), 
     name='password_reset_complete'),
    
    path('test-smtp/', views.test_smtp, name='test_smtp'),

path('debug-cart/', views.debug_cart, name='debug_cart'),

]

