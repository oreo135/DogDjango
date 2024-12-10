from django.core.mail import send_mail

def send_pet_creation_email(user, pet_name):
    send_mail(
        'Новый питомец добавлен!',
        f'Здравствуйте, {user.username}! Ваш питомец "{pet_name}" успешно добавлен в систему.',
        'no-reply@example.com',
        [user.email],
        fail_silently=False,
    )
