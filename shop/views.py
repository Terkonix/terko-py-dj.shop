from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review
from .forms import ReviewForm, CheckoutForm


def home(request):
    """Головна сторінка з рекомендованими товарами"""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    categories = Category.objects.all()[:6]
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'shop/home.html', context)


def product_list(request, category_slug=None):
    """Список товарів з фільтрацією по категоріях"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Пошук
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Сортування
    sort_by = request.GET.get('sort', 'created_at')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, product_slug):
    """Детальна сторінка товару"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    reviews = Review.objects.filter(product=product, is_approved=True)
    
    # Форма відгуку
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Ваш відгук було додано!')
            return redirect('product_detail', product_slug=product.slug)
    else:
        form = ReviewForm()
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'shop/product_detail.html', context)


@login_required
def cart_view(request):
    """Перегляд кошика"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/cart.html', context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    """Додавання товару в кошик"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Товар додано в кошик',
            'cart_total': cart.total_items
        })
    
    messages.success(request, f'{product.name} додано в кошик')
    return redirect('product_detail', product_slug=product.slug)


@login_required
@require_POST
def update_cart_item(request, item_id):
    """Оновлення кількості товару в кошику"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        message = 'Товар видалено з кошика'
    else:
        cart_item.quantity = quantity
        cart_item.save()
        message = 'Кількість оновлено'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_total': cart_item.cart.total_items,
            'item_total': cart_item.total_price,
            'cart_total_price': cart_item.cart.total_price
        })
    
    messages.success(request, message)
    return redirect('cart_view')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    """Видалення товару з кошика"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} видалено з кошика',
            'cart_total': Cart.objects.get(user=request.user).total_items
        })
    
    messages.success(request, f'{product_name} видалено з кошика')
    return redirect('cart_view')


@login_required
def checkout(request):
    """Оформлення замовлення"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        messages.warning(request, 'Ваш кошик порожній')
        return redirect('cart_view')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Створюємо замовлення
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.total_price,
                shipping_address=form.cleaned_data['shipping_address'],
                shipping_city=form.cleaned_data['shipping_city'],
                shipping_zip_code=form.cleaned_data['shipping_zip_code'],
                shipping_phone=form.cleaned_data['shipping_phone'],
                notes=form.cleaned_data.get('notes', '')
            )
            
            # Додаємо товари в замовлення
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.final_price,
                    total_price=cart_item.total_price
                )
            
            # Очищуємо кошик
            cart_items.delete()
            
            messages.success(request, f'Замовлення #{order.order_number} створено успішно!')
            return redirect('order_detail', order_id=order.id)
    else:
        form = CheckoutForm()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'form': form,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def order_list(request):
    """Список замовлень користувача"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """Деталі замовлення"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'shop/order_detail.html', context)


def search(request):
    """Пошук товарів"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    # Пагінація
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'shop/search.html', context)