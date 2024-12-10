from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    help = "Create a PostgreSQL database and user"

    def handle(self, *args, **kwargs):
        try:
            # Проверяем, существует ли база данных
            check_db_command = [
                'sudo', 'psql',
                '-h', 'localhost',
                '-U', 'postgres',
                '-tAc', "SELECT 1 FROM pg_database WHERE datname='django_db';"
            ]
            result = subprocess.run(check_db_command, capture_output=True, text=True, check=True)
            if result.stdout.strip() == '1':
                self.stdout.write(self.style.WARNING("Database 'django_db' already exists."))
            else:
                # Создаём базу данных
                subprocess.run([
                    'sudo', 'psql',
                    '-h', 'localhost',
                    '-U', 'postgres',
                    '-c', "CREATE DATABASE django_db;"
                ], check=True)
                self.stdout.write(self.style.SUCCESS("Database 'django_db' created successfully."))

            # Проверяем, существует ли пользователь
            check_user_command = [
                'sudo', 'psql',
                '-h', 'localhost',
                '-U', 'postgres',
                '-tAc', "SELECT 1 FROM pg_roles WHERE rolname='dog_user';"
            ]
            result = subprocess.run(check_user_command, capture_output=True, text=True, check=True)
            if result.stdout.strip() == '1':
                self.stdout.write(self.style.WARNING("User 'dog_user' already exists."))
            else:
                # Создаём пользователя
                subprocess.run([
                    'sudo', 'psql',
                    '-h', 'localhost',
                    '-U', 'postgres',
                    '-c', "CREATE USER dog_user WITH PASSWORD 'dog_pass';"
                ], check=True)
                self.stdout.write(self.style.SUCCESS("User 'dog_user' created successfully."))

            # Назначаем права
            subprocess.run([
                'sudo', 'psql',
                '-h', 'localhost',
                '-U', 'postgres',
                '-c', "GRANT ALL PRIVILEGES ON DATABASE django_db TO dog_user;"
            ], check=True)
            self.stdout.write(self.style.SUCCESS("Privileges granted successfully."))
        except subprocess.CalledProcessError as e:
            self.stderr.write(self.style.ERROR(f"Command failed: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error: {e}"))
