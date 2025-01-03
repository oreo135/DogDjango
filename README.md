# My Django Project

## Описание
Проект создан для управления пользователями, собаками и породами. Включает функционал для просмотра профилей, отзывов, а также поиск по собакам и породам.

## Основные функции:
1. Управление пользователями:
    - Регистрация, авторизация и личный кабинет.
    - Возможность оставлять отзывы.
2. Управление собаками:
    - Добавление, редактирование и удаление собак.
    - Поиск по имени собаки или породе.
3. Поиск по породам.

## Запуск проекта:
1. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
2. Выполните миграции базы данных:
    ```bash
    python manage.py migrate
    ```
3. Создайте суперпользователя:
    ```bash
    python manage.py createsuperuser
    ```
4. Запустите сервер разработки:
    ```bash
    python manage.py runserver
    ```
5. Перейдите по адресу:
    - Главная страница: `http://127.0.0.1:8000/`
    - Админка: `http://127.0.0.1:8000/admin/`

## Структура проекта:
- `users/` - Модуль для работы с пользователями и отзывами.
- `dogs/` - Модуль для работы с собаками и породами.
- `templates/` - HTML-шаблоны для отображения страниц.

## Требования:
- Python 3.10+
- Django 5.1.4
- PostgreSQL

