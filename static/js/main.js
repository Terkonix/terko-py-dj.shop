// Terko Shop - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Ініціалізація всіх компонентів
    initCart();
    initSearch();
    initAlerts();
    initAnimations();
});

// Функції для роботи з кошиком
function initCart() {
    // Додавання товару в кошик
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.dataset.productId;
            const originalText = this.innerHTML;
            
            // Показуємо стан завантаження
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Додавання...';
            this.disabled = true;
            
            addToCart(productId, this, originalText);
        });
    });
}

function addToCart(productId, button, originalText) {
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Оновлюємо лічильник кошика
            updateCartCount(data.cart_total);
            
            // Показуємо повідомлення
            showAlert('success', data.message);
            
            // Анімація кнопки
            animateButton(button, 'success');
        } else {
            showAlert('danger', 'Помилка при додаванні товару');
            animateButton(button, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Помилка при додаванні товару');
        animateButton(button, 'error');
    })
    .finally(() => {
        // Відновлюємо кнопку
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function updateCartCount(count) {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        cartCount.textContent = count;
        
        // Анімація оновлення лічильника
        cartCount.classList.add('animate__animated', 'animate__bounce');
        setTimeout(() => {
            cartCount.classList.remove('animate__animated', 'animate__bounce');
        }, 1000);
    }
}

function animateButton(button, type) {
    const classes = type === 'success' ? 'btn-success' : 'btn-danger';
    const originalClasses = button.className;
    
    button.className = button.className.replace(/btn-\w+/, classes);
    
    setTimeout(() => {
        button.className = originalClasses;
    }, 2000);
}

// Функції для пошуку
function initSearch() {
    const searchInput = document.querySelector('input[name="q"]');
    const searchForm = document.querySelector('form[action*="search"]');
    
    if (searchInput && searchForm) {
        // Автодоповнення пошуку
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
        
        // Обробка форми пошуку
        searchForm.addEventListener('submit', function(e) {
            const query = searchInput.value.trim();
            if (!query) {
                e.preventDefault();
                showAlert('warning', 'Введіть пошуковий запит');
            }
        });
    }
}

function performSearch(query) {
    if (query.length < 2) return;
    
    // Тут можна додати AJAX пошук з автодоповненням
    console.log('Searching for:', query);
}

// Функції для повідомлень
function initAlerts() {
    // Автоматичне прибирання повідомлень
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
    });
}

function showAlert(type, message, duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Анімація появи
        alertDiv.classList.add('fade-in');
        
        // Автоматичне прибирання
        if (duration > 0) {
            setTimeout(() => {
                alertDiv.remove();
            }, duration);
        }
    }
}

// Функції анімації
function initAnimations() {
    // Анімація при прокрутці
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Спостерігаємо за елементами
    const animatedElements = document.querySelectorAll('.product-card, .category-card, .feature-box');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// Утилітарні функції
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function formatPrice(price) {
    return new Intl.NumberFormat('uk-UA', {
        style: 'currency',
        currency: 'UAH',
        minimumFractionDigits: 0
    }).format(price);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Функції для роботи з кошиком (для сторінки кошика)
function updateCartItemQuantity(itemId, quantity) {
    if (quantity < 1) {
        removeCartItem(itemId);
        return;
    }
    
    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Оновлюємо ціну елемента
            const itemElement = document.querySelector(`[data-item-id="${itemId}"]`);
            const totalElement = itemElement.querySelector('.item-total');
            if (totalElement) {
                totalElement.textContent = formatPrice(data.item_total);
            }

            // Оновлюємо загальну кількість та ціну
            updateCartTotals(data.cart_total, data.cart_total_price);
            showAlert('success', data.message);
        } else {
            showAlert('danger', 'Помилка при оновленні кошика');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'Помилка при оновленні кошика');
    });
}

function removeCartItem(itemId) {
    if (confirm('Ви впевнені, що хочете видалити цей товар з кошика?')) {
        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Видаляємо елемент з DOM
                const itemElement = document.querySelector(`[data-item-id="${itemId}"]`);
                if (itemElement) {
                    itemElement.style.animation = 'slideOut 0.3s ease-out';
                    setTimeout(() => {
                        itemElement.remove();
                    }, 300);
                }

                // Оновлюємо загальну кількість та ціну
                updateCartTotals(data.cart_total, data.cart_total_price);

                // Якщо кошик порожній, перезавантажуємо сторінку
                if (data.cart_total == 0) {
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                }

                showAlert('success', data.message);
            } else {
                showAlert('danger', 'Помилка при видаленні товару');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('danger', 'Помилка при видаленні товару');
        });
    }
}

function updateCartTotals(totalItems, totalPrice) {
    const totalItemsElement = document.getElementById('total-items');
    const subtotalElement = document.getElementById('subtotal');
    const totalPriceElement = document.getElementById('total-price');
    
    if (totalItemsElement) totalItemsElement.textContent = totalItems;
    if (subtotalElement) subtotalElement.textContent = formatPrice(totalPrice);
    if (totalPriceElement) totalPriceElement.textContent = formatPrice(totalPrice);
    
    // Оновлюємо лічильник в навігації
    updateCartCount(totalItems);
}

// CSS анімації
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(-100%);
        }
    }
    
    .animate__animated {
        animation-duration: 1s;
        animation-fill-mode: both;
    }
    
    .animate__bounce {
        animation-name: bounce;
    }
    
    @keyframes bounce {
        0%, 20%, 53%, 80%, 100% {
            animation-timing-function: cubic-bezier(0.215, 0.610, 0.355, 1.000);
            transform: translate3d(0,0,0);
        }
        40%, 43% {
            animation-timing-function: cubic-bezier(0.755, 0.050, 0.855, 0.060);
            transform: translate3d(0, -30px, 0);
        }
        70% {
            animation-timing-function: cubic-bezier(0.755, 0.050, 0.855, 0.060);
            transform: translate3d(0, -15px, 0);
        }
        90% {
            transform: translate3d(0,-4px,0);
        }
    }
`;
document.head.appendChild(style);
