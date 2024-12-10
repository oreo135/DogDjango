from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Dog
from .forms import DogForm, PedigreeFormSet
from django.core.cache import cache
from django.http import HttpResponse
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

class DogCreateView(CreateView):
    """
    Создание новой собаки.
    """
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_form.html'
    success_url = reverse_lazy('dogs:list_dogs')

    def get_context_data(self, **kwargs):
        """
        Добавляем в контекст форму для редактирования родословной (PedigreeFormSet).
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['pedigree_formset'] = PedigreeFormSet(self.request.POST, instance=self.object)
        else:
            context['pedigree_formset'] = PedigreeFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        """
        Обрабатываем форму Dog и PedigreeFormSet, если обе формы валидны.
        """
        # Сохраняем объект Dog
        self.object = form.save()
        # Получаем форму PedigreeFormSet из контекста
        context = self.get_context_data()
        pedigree_formset = context['pedigree_formset']

        if pedigree_formset.is_valid():
            # Устанавливаем связь Pedigree с текущим Dog
            pedigree_formset.instance = self.object
            # Сохраняем родословную
            pedigree_formset.save()
            # Отправляем письмо о создании питомца
            send_pet_creation_email(self.request.user, self.object.name)
            return super().form_valid(form)
        else:
            # Если родословная не валидна, возвращаем ошибку
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

    def form_invalid(self, form):
        """
        Обрабатываем ошибки формы.
        """
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

def test_cache_view(request):
    cache.set('test_key', 'Hello, Redis!', timeout=30)  # Сохраняем данные на 30 секунд
    value = cache.get('test_key')
    return HttpResponse(f"Ключ из кэша: {value}")