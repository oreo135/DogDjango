from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import (TemplateView, UpdateView, CreateView,
                                  DetailView, ListView, FormView)
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from .models import CustomUser, Review
from .forms import RegisterForm, UpdateProfileForm, ReviewForm
from .utils import generate_random_password
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden


class CustomLoginView(LoginView):
    """
    Вход пользователя.
    """
    template_name = 'users/login.html'

    def form_valid(self, form):
        """
        Логика при успешной авторизации.
        """
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f'Добро пожаловать, {user.username}!')
        return redirect('users:user_profile', username=user.username)

    def form_invalid(self, form):
        """
        Логика при ошибках авторизации.
        """
        messages.error(self.request, 'Ошибка при заполнении формы.')
        return super().form_invalid(form)


class UserProfileView(LoginRequiredMixin, DetailView, FormView):
    """
    Просмотр профиля пользователя с отображением отзывов и формой для добавления отзыва.
    """
    model = CustomUser
    template_name = 'users/user_profile.html'
    context_object_name = 'user'
    form_class = ReviewForm

    def get_object(self, queryset=None):
        """
        Получение профиля пользователя.
        """
        return get_object_or_404(CustomUser, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        """
        Добавляем отзывы и форму в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(user=self.object)  # Отзывы для текущего пользователя
        context['review_form'] = self.get_form()
        context['is_own_profile'] = self.object == self.request.user  # Проверка на владельца профиля
        return context

    def form_valid(self, form):
        """
        Обработка формы добавления отзыва.
        """
        form.instance.author = self.request.user
        form.instance.user = self.get_object()
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """
        Перенаправление на профиль после добавления отзыва.
        """
        user = self.get_object()
        return reverse('users:user_profile', kwargs={'username': user.username})


class RegisterView(CreateView):
    """
    Регистрация нового пользователя.
    """
    model = CustomUser
    form_class = RegisterForm
    template_name = 'users/user_register.html'

    def get_success_url(self):
        return reverse_lazy('users:user_profile', kwargs={'username': self.object.username})


    def form_valid(self, form):
        """
        Логика при успешной регистрации.
        """
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()

        send_mail(
            'Добро пожаловать!',
            f'Здравствуйте, {user.username}!\nВаш аккаунт успешно создан.',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )
        login(self.request, user)
        messages.success(self.request, f'Регистрация прошла успешно! Добро пожаловать, {user.username}.')
        # Устанавливаем self.object для корректной работы get_success_url()
        self.object = user
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """
        Логика при ошибках регистрации.
        """
        messages.error(self.request, 'Исправьте ошибки в форме.')
        return super().form_invalid(form)


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """
    Обновление профиля пользователя.
    """
    model = CustomUser
    form_class = UpdateProfileForm
    template_name = 'users/user_update_profile.html'

    def get_object(self, queryset=None):
        """
        Возвращаем текущего пользователя.
        """
        username = self.kwargs.get('username')
        if self.request.user.username != username:
            messages.error(self.request, 'Вы можете редактировать только свой профиль.')
            return self.request.user
        return self.request.user

    def form_valid(self, form):
        """
        Логика при успешном обновлении.
        """
        messages.success(self.request, 'Ваш профиль успешно обновлён.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Логика при ошибках.
        """
        messages.error(self.request, 'Исправьте ошибки в форме.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('users:user_profile', kwargs={'username': self.object.username})


class ManagePasswordView(LoginRequiredMixin, TemplateView):
    """
    Управление паролем пользователя.
    """
    template_name = 'users/manage_password.html'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'manual':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not new_password or len(new_password) < 8:
                messages.error(request, 'Пароль должен содержать минимум 8 символов.')
            elif new_password != confirm_password:
                messages.error(request, 'Пароли не совпадают.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Ваш пароль успешно изменён.')
                return redirect('users:user_profile', username=request.user.username)
        elif action == 'generate':
            new_password = generate_random_password()
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

            send_mail(
                'Ваш новый пароль',
                f'Здравствуйте, {request.user.username}!\nВаш новый пароль: {new_password}',
                'your-email@gmail.com',
                [request.user.email],
                fail_silently=False,
            )
            messages.success(request, 'Ваш пароль был сброшен. Новый пароль отправлен на вашу почту.')
            return redirect('users:user_profile', username=request.user.username)
        return super().get(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    """
    Класс представления для выхода из аккаунта.
    """
    next_page = reverse_lazy('users:login')  # Перенаправление после выхода

    def dispatch(self, request, *args, **kwargs):
        """
        Добавляем сообщение при выходе.
        """
        messages.success(request, 'Вы успешно вышли из аккаунта.')
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(UserPassesTestMixin):
    """
    Миксин для проверки, что пользователь является администратором.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()

    def handle_no_permission(self):
        return HttpResponseForbidden("Доступ запрещен.")


class ManageUsersView(AdminRequiredMixin, ListView):
    """
    Управление пользователями (только для администраторов).
    """
    model = CustomUser
    template_name = 'users/manage_users.html'
    context_object_name = 'users'

    def get_queryset(self):
        """
        Исключаем администраторов из списка пользователей.
        """
        return CustomUser.objects.exclude(role='admin')

class UserListView(ListView):
    """
    Список всех пользователей.
    """
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10  # Количество пользователей на странице (опционально)


class ReviewListView(ListView):
    """
    Список отзывов для пользователя с пагинацией.
    """
    model = Review
    template_name = 'users/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 5  # Пагинация: 5 отзывов на странице

    def get_queryset(self):
        # Фильтруем отзывы для конкретного пользователя
        user = get_object_or_404(CustomUser, username=self.kwargs['username'])
        return Review.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        # Добавляем информацию о пользователе, для которого показываются отзывы
        context = super().get_context_data(**kwargs)
        context['reviewed_user'] = get_object_or_404(CustomUser, username=self.kwargs['username'])
        return context


class ReviewCreateView(CreateView):
    """
    Создание нового отзыва для пользователя.
    """
    model = Review
    form_class = ReviewForm
    template_name = 'users/review_form.html'

    def form_valid(self, form):
        # Устанавливаем автора отзыва и пользователя, к которому относится отзыв
        form.instance.author = self.request.user
        form.instance.user = get_object_or_404(CustomUser, username=self.kwargs['username'])
        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем обратно на страницу отзывов пользователя
        return f"/users/{self.kwargs['username']}/reviews/"


class ReviewDetailView(DetailView):
    """
    Детали отзыва.
    """
    model = Review
    template_name = 'users/review_detail.html'
    context_object_name = 'review'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'