# accounts/context_processors.py
from .models import Product

def cart_context(request):
    cart_count = request.session.get('cart_count', 0)
    cart_total = request.session.get('cart_total', 0)
    cart = request.session.get('cart', {})
    
    # Get actual product details
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