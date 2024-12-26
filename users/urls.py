from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    CustomLoginView, UserProfileView, RegisterView,
    UpdateProfileView, ManagePasswordView, CustomLogoutView,
    ManageUsersView, UserListView, ReviewListView, ReviewCreateView
)

app_name = 'users'  # Указываем app_name

urlpatterns = [
    path('profile/<str:username>/', UserProfileView.as_view(), name='user_profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/<str:username>/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/<str:username>/manage_password/', ManagePasswordView.as_view(), name='manage_password'),
    path('manage-users/', ManageUsersView.as_view(), name='manage_users'),
    path('', UserListView.as_view(), name='user_list'),  # Список пользователей
    path('<str:username>/reviews/', ReviewListView.as_view(), name='user_reviews'),
    path('<str:username>/add_review/', ReviewCreateView.as_view(), name='add_review'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
