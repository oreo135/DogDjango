from django.urls import path
from .views import (DogListView,
                    DogDetailView,
                    DogCreateView,
                    DogUpdateView,
                    DogDeleteView,
                    test_cache_view,
                    DogSearchListView,
                    BreedSearchListView,)

app_name = 'dogs'

urlpatterns = [
    path('', DogListView.as_view(), name='list_dogs'),  # Список собак
    path('create/', DogCreateView.as_view(), name='create_dog'),  # Добавить собаку
    path('<int:pk>/', DogDetailView.as_view(), name='dog_detail'),  # Просмотр собаки
    path('<int:pk>/update/', DogUpdateView.as_view(), name='update_dog'),  # Редактирование собаки
    path('<int:pk>/delete/', DogDeleteView.as_view(), name='delete_dog'),  # Удаление собаки
    path('test-cache/', test_cache_view, name='test_cache'),  # URL для тестирования Redis
    path('search/dogs/', DogSearchListView.as_view(), name='dog_search'),
    path('search/breeds/', BreedSearchListView.as_view(), name='breed_search'),
]