from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import F
from .models import Dog, Pedigree, Breed
from .forms import DogForm, get_pedigree_formset
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .utils import send_pet_creation_email


class DogListView(ListView):
    """
    Список всех собак.
    """
    model = Dog
    template_name = 'dogs/dog_list.html'
    context_object_name = 'dogs'

class DogDetailView(DetailView):
    """
    Просмотр информации о собаке.
    """
    model = Dog
    template_name = 'dogs/dog_detail.html'
    context_object_name = 'dog'

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Отладка: выводим владельца и текущего пользователя
        print(f"Owner of the dog: {self.object.owner}")
        print(f"Current user: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")

        # Увеличиваем счётчик просмотров, если текущий пользователь не владелец
        if (not request.user.is_authenticated or self.object.owner != request.user):
            Dog.objects.filter(pk=self.object.pk).update(views=F('views') + 1)
            # Проверяем кратность просмотров сразу в БД
            updated_dog = Dog.objects.get(pk=self.object.pk)
            if updated_dog.views % 100 == 0:
                updated_dog.send_notification_if_needed()
        else:
           print("No changes to views counter.")

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Добавляем информацию о родословной в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['pedigree'] = Pedigree.objects.filter(pet=self.object)  # Связанная родословная
        return context

class DogCreateView(CreateView):
    """
    Создание новой собаки.
    """
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_form.html'
    success_url = reverse_lazy('dogs:list_dogs')

    def get_form(self, form_class=None):
        """
        Убираем ненужные поля при создании.
        """
        form = super().get_form(form_class)
        # Убираем поля 'is_active', 'owner', 'views' при создании
        for field in ['is_active', 'owner', 'views']:
            if field in form.fields:
                del form.fields[field]
        return form

    def get_context_data(self, **kwargs):
        """
        Добавляем в контекст форму для редактирования родословной (PedigreeFormSet).
        """
        context = super().get_context_data(**kwargs)
        PedigreeFormSet = get_pedigree_formset()
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, instance=self.object)
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.object)
        context['is_update'] = False
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        """
        Устанавливаем дополнительные поля при создании собаки.
        """
        print("Форма основная валидна")
        # Автоматически устанавливаем владельца и значения по умолчанию
        form.instance.owner = self.request.user
        form.instance.is_active = True  # По умолчанию собака активна
        form.instance.views = 0  # Начальное количество просмотров

        # Сохраняем собаку
        self.object = form.save()

        # Обрабатываем родословную
        context = self.get_context_data()
        pedigree_formset = context['pedigree_formset']

        if pedigree_formset.is_valid():
            print("Форма родословной валидна")
            pedigree_formset.instance = self.object
            pedigree_formset.save()
            send_pet_creation_email(self.request.user, self.object.name)
            return super().form_valid(form)
        else:
            print("Форма родословной не валидна:", pedigree_formset.errors)
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Обрабатываем ошибки формы.
        """
        messages.error(self.request, 'Исправьте ошибки в форме.')
        return super().form_invalid(form)


class DogUpdateView(UpdateView):
    """
    Редактирование собаки.
    """
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_form.html'
    success_url = reverse_lazy('dogs:list_dogs')


    def get_form(self, form_class=None):
        """
        Ограничиваем отображаемые и редактируемые поля в зависимости от роли пользователя.
        """
        form = super().get_form(form_class)
        user = self.request.user

        if user.role not in ['admin', 'moderator']:
            # Убираем поля для обычных пользователей
            for field in ['is_active', 'owner', 'views']:
                if field in form.fields:
                    del form.fields[field]
        else:
            # Делаем поля только для чтения для админов и модераторов
            for field in ['is_active', 'owner', 'views']:
                if field in form.fields:
                    form.fields[field].widget.attrs['disabled'] = True
        return form

    def get_context_data(self, **kwargs):
        """
        Добавляем родословную в контекст.
        """
        context = super().get_context_data(**kwargs)
        PedigreeFormSet = get_pedigree_formset(instance=self.object)
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, instance=self.object)
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.object)
        context['is_update'] = True
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        """
        Обрабатываем форму Dog и родословную.
        """
        print("Форма валидна и данные сохранены.")

        context = self.get_context_data()
        pedigree_formset = context['pedigree_formset']

        if pedigree_formset.is_valid():
            self.object = form.save()
            pedigree_formset.instance = self.object
            pedigree_formset.save()
            messages.success(self.request, 'Собака успешно обновлена.')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Исправьте ошибки в родословной.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Обрабатываем ошибки формы.
        """
        print("Форма невалидна. Ошибки:", form.errors)
        messages.error(self.request, 'Исправьте ошибки в форме.')
        return super().form_invalid(form)

class DogDeleteView(DeleteView):
    """
    Удаление собаки.
    """
    model = Dog
    template_name = 'dogs/dog_confirm_delete.html'
    success_url = reverse_lazy('dogs:list_dogs')

    def post(self, request, *args, **kwargs):
        """
        Добавляем сообщение об успешном удалении.
        """
        messages.success(self.request, 'Собака успешно удалена.')
        return super().post(request, *args, **kwargs)


class DogSearchListView(ListView):
    model = Dog
    template_name = 'dogs/dog_search.html'
    context_object_name = 'dogs'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Dog.objects.filter(Q(name__icontains=query) | Q(breed__name__icontains=query))
        return Dog.objects.all()

class BreedSearchListView(ListView):
    model = Breed
    template_name = 'dogs/breed_search.html'
    context_object_name = 'breeds'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Breed.objects.filter(name__icontains=query)
        return Breed.objects.all()

def test_cache_view(request):
    cache.set('test_key', 'Hello, Redis!', timeout=30)  # Сохраняем данные на 30 секунд
    value = cache.get('test_key')
    return HttpResponse(f"Ключ из кэша: {value}")