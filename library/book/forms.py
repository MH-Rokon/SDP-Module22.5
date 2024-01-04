from .models import Book
from django import forms

class PostForm(forms.ModelForm):
    
    class Meta:
        model = Book
        fields = '__all__'
       