from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = "Изменение роли пользователя"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help="Имя пользователя")
        parser.add_argument('role', type=str, choices=['admin', 'moderator', 'user'], help="Новая роль")

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        role = kwargs['role']
        try:
            user = CustomUser.objects.get(username=username)
            if user.is_admin():
                self.stdout.write(self.style.ERROR('Нельзя изменить роль администратора.'))
                return
            user.role = role
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Роль пользователя {username} изменена на {role}"))
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Пользователь {username} не найден."))
