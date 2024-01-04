from django.db import models
from django.contrib.auth.models import User






class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='upload/', null=True, blank=True)  
    borrowing_price = models.DecimalField(max_digits=10, decimal_places=2)
    user_reviews = models.TextField(blank=True)
    categories = models.ManyToManyField(Category)
    user = models.ForeignKey(User, related_name='books', on_delete=models.CASCADE)
    

    def __str__(self):
        return self.title
    



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    saved_books = models.ManyToManyField(Book)

    def __str__(self):
        return self.user.username





