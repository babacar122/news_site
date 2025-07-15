from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Article, Category
from .forms import ArticleForm

class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    ordering = ['-pub_date']
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_published=True)
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_articles'] = Article.objects.filter(
            category=self.object.category,
            is_published=True
        ).exclude(pk=self.object.pk)[:3]
        return context

class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    
    def test_func(self):
        return self.request.user.is_editor()
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_published = True 
        messages.success(self.request, "L'article a été créé et publié avec succès.")
        return super().form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    
    def test_func(self):
        article = self.get_object()
        return self.request.user.is_editor() and (self.request.user == article.author or self.request.user.is_admin())

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'articles/article_confirm_delete.html'
    success_url = reverse_lazy('article_list')
    
    def test_func(self):
        article = self.get_object()
        return self.request.user.is_editor() and (self.request.user == article.author or self.request.user.is_admin())

def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    articles = Article.objects.filter(category=category, is_published=True).order_by('-pub_date')
    return render(request, 'articles/category_articles.html', {
        'category': category,
        'articles': articles
    })