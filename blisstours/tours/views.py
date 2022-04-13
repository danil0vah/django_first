from django.contrib.auth import logout, login
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404 
from django.views.generic import ListView, DetailView, CreateView 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, FormView

from django.urls import reverse_lazy
from .forms import AddPostForm, RegisterUserForm, LoginUserForm, ContactUserForm
from .models import Categories, Tours
from .utils import DataMixin, menu


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'tours/register.html'
    success_url = reverse_lazy('login')
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        return dict(list(context.items()) + list(c_def.items()))

# можно и так
#    def form_valid(self, form):
#        user = form.save()
#        login(self.request, user)
#        return redirect('home')

    def get_success_url(self):
        print(self.object)
        login(self.request, self.object)
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'tours/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        return context | c_def

    def get_success_url(self):
        return reverse_lazy('home')


class ToursHome(DataMixin, ListView):
    model = Tours
    template_name = 'tours/index.html'
    context_object_name = 'tours'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Главная страница')
        return context | c_def

    def get_queryset(self):
        return Tours.objects.filter(is_published=True).select_related('cat_id')


def index(request):
    posts = Tours.objects.all().order_by('-time_update')
    cats = Categories.objects.all()
    context = {
        'tours': posts,
        'title': 'Главная страница',
        'cat_selected': 0,
        'cats': cats
    }
    return render(request, 'tours/index.html', context)


class ToursCategory(DataMixin, ListView):
    model = Tours
    template_name = 'tours/index.html'
    context_object_name = 'tours'
    allow_empty = False

    def get_queryset(self):
        return Tours.objects.filter(cat_id__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat_id')
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Categories.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория -' + c.name,
                                        cat_selected=c.slug)
        return context | c_def


def showcategory(request, cat_slug):
    posts = Tours.objects.filter(cat_id__slug=cat_slug).order_by('-time_update')

    if len(posts) == 0:
        raise Http404()

    context = {
        'tours': posts,
        'title': 'Главная страница',
        'cat_selected': cat_slug,
    }
    return render(request, 'tours/index.html', context)


class ShowPost(DataMixin, DetailView):
    model = Tours
    template_name = 'tours/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'tour'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['tour'])
        return context.update(c_def)
        

def showpost(request, post_slug):
    post = get_object_or_404(Tours, slug=post_slug)

    context = {
        'menu': menu,
        'tour': post,
        'title': post.title,
        'cat_selected': post.cat_id,
    }
    return render(request, 'tours/post.html', context)


def about(request):
    return render(request, 'tours/about.html')


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'tours/addpage.html'
    success_url = reverse_lazy('home')
    raise_exception = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Добавление статьи')
        return context | c_def


def addpage(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:   
        form = AddPostForm()
    
    context = {'menu': menu, 'form': form, 'title': 'Добавление статьи'}

    return render(request, 'tours/addpage.html', context=context)


class ContactFormView(DataMixin, FormView):
    form_class = ContactUserForm
    template_name = 'tours/contacts.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        c_def = self.get_user_context(title='Обратная связь')
        return context | c_def

    def form_valid(self, form):
        print(form.cleaned_data)
        return redirect('home')

    def get_success_url(self):
        return reverse_lazy('home')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')

