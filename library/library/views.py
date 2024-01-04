from django.shortcuts import render, redirect
from  book.models import Book, Category
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from accounts  import forms, models

def home(request):
    data = Book.objects.all()
    return render(request, 'home2.html', {'data': data})

@login_required
def book(request):
    data = Book.objects.all()
    return render(request, 'home.html', {'data': data})

@login_required
def it(request):
    category_instance = Category.objects.get(name='IT')  
    data = Book.objects.filter(categories=category_instance)
    return render(request, 'it.html', {'data': data})
#
@login_required
def tragedy(request):
    category_instance = Category.objects.get(name='Tragedy')  
    data = Book.objects.filter(categories=category_instance)
    return render(request, 'tragedy.html', {'data': data})

@login_required
def drama(request):
    category_instance = Category.objects.get(name='Drama') 
    data = Book.objects.filter(categories=category_instance)
    return render(request, 'drama.html', {'data': data})

@login_required
def all(request):
    data = Book.objects.all()
    return render(request, 'all.html', {'data': data})

@login_required
def add_book(request, id):
    book = models.Book.objects.get(pk=id) 
    book_form = forms.BookForm(instance=book)
    if request.method == 'POST': 
        book_form = forms.BookForm(request.POST, instance=book)
        if book_form.is_valid(): 
            book_form.instance.author = request.user
            book_form.save() 
            return redirect('profile') 
    
    return render(request, 'add_book.html', {'form': book_form})
