from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, UpdateView, CreateView, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from .models import CustomUser
from .forms import RegisterForm, UpdateProfileForm
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


class UserProfileView(LoginRequiredMixin, DetailView):
    """
    Просмотр профиля пользователя.
    """
    model = CustomUser
    template_name = 'users/user_profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        """
        Проверяем, что пользователь просматривает свой профиль.
        """
        username = self.kwargs.get('username')
        if self.request.user.username != username:
            return get_object_or_404(CustomUser, username=self.request.user.username)
        return get_object_or_404(CustomUser, username=username)

    def get_context_data(self, **kwargs):
        """
        Добавляем в контекст флаг, чтобы различать свой профиль и чужой.
        """
        context = super().get_context_data(**kwargs)
        context['is_own_profile'] = self.object == self.request.user
        return context


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