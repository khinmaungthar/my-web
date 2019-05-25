from django.contrib import admin
from .models import Books,BorrowBooks

admin.site.register(Books)
admin.site.register(BorrowBooks)