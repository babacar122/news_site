from django import forms
from .models import Article, Category

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'image', 'image_caption', 'summary', 'content', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'summary': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['content'].required = False