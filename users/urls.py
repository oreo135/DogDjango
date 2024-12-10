from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    CustomLoginView, UserProfileView, RegisterView,
    UpdateProfileView, ManagePasswordView, CustomLogoutView, ManageUsersView
)


urlpatterns = [
    # Просмотр профиля пользователя
    path('profile/<str:username>/', UserProfileView.as_view(), name='user_profile'),

    # Регистрация пользователя
    path('register/', RegisterView.as_view(), name='register'),

    # Авторизация пользователя
    path('login/', CustomLoginView.as_view(), name='login'),

    # Обновление профиля
    path('profile/<str:username>/update/', UpdateProfileView.as_view(), name='update_profile'),

    # Выход из аккаунта
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Управление паролем (с использованием username)
    path('profile/<str:username>/manage_password/', ManagePasswordView.as_view(), name='manage_password'),
    path('manage-users/', ManageUsersView.as_view(), name='manage_users'),
]

# Настройка для медиа-файлов
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
