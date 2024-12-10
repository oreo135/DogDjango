from django.shortcuts import render

def home_view(request):
    """
    Представление для главной страницы проекта.
    """
    return render(request, 'home/homik.html')
