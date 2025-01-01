from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db import models
from django.urls import reverse
import uuid

class CustomUser(AbstractUser):
    """
    Расширенная модель пользователя.

    Атрибуты:
        role (CharField): Роль пользователя с предопределёнными значениями (admin, moderator, user).
        age (IntegerField): Возраст пользователя (может быть пустым).
        bio (TextField): Краткая биография пользователя (опционально).
        avatar (ImageField): Аватар пользователя (опционально).
        birth_date (DateField): Дата рождения пользователя (опционально).
    """

    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    ]
    is_active = models.BooleanField(default=True, verbose_name='Активный пользователь')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    age = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateField(blank=True, null=True)


    def get_role_display(self) -> str:
        """
        Возвращает отображаемое имя роли.
        """
        return dict(self.ROLE_CHOICES).get(self.role, "Неизвестная роль")

    def __str__(self):
        """
        Возвращает строковое представление пользователя (имя пользователя).
        """
        return f"{self.username} ({self.get_role_display()})"

    def is_admin(self):
        """
        Проверка, является ли пользователь администратором.
        """
        return self.role == 'admin'

    def is_moderator(self):
        """
        Проверка, является ли пользователь модератором.
        """
        return self.role == 'moderator'

    def is_user(self):
        """
        Проверка, является ли пользователь обычным пользователем.
        """
        return self.role == 'user'

    def get_absolute_url(self):
        """
        Возвращает URL страницы профиля пользователя.
        """
        return reverse('users:user_profile', kwargs={'username': self.username})

class Review(models.Model):
    """
    Модель для отзывов.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='review_author')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.PositiveIntegerField(verbose_name='Рейтинг', default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, verbose_name='Ссылка')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.author.username}-{uuid.uuid4().hex[:6]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Отзыв от {self.author.username} для {self.user.username}"

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'