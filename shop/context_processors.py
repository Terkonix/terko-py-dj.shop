from .models import Category


def categories(request):
    """Контекстний процесор для додавання категорій до всіх шаблонів"""
    return {
        'categories': Category.objects.all()[:6]  # Показуємо тільки перші 6 категорій в навігації
    }
