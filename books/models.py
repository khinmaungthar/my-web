from django.db import models
from django.contrib.auth.models import User

from django.conf import settings
# Create your models here.

class Books(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    publisher = models.CharField(max_length=50)
    photo = models.FileField()
    summary = models.CharField(max_length=2000)
    releaseDate = models.DateField()
    borrowStatus = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Book: ' + self.title

    class Meta:
        ordering = ['title']
        db_table = "Books"
        verbose_name = "Book"
        verbose_name_plural = "Books"


# Create your models here.
class BorrowBooks(models.Model):

    book = models.ForeignKey('Books', null=True, blank=True, on_delete=models.PROTECT)
    borrowBy = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    #borrowBy = models.CharField(max_length=50)
    borrowDate = models.DateTimeField(null=True, blank=True)
    dueDate = models.DateTimeField(null=True, blank=True)
    returnDate = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)
    def __unicode__(self):
        return 'BooksLoan: ' + self.book

    class Meta:
        get_latest_by = "borrowDate"
        db_table = "BorrowBooks"
        verbose_name = "BorrowBooks"
        verbose_name_plural = "BorrowBooks"
