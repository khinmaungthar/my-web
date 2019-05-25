from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from .models import Books,BorrowBooks
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re
from django.contrib import messages
from datetime import datetime,date, timedelta
from django.utils import timezone
import json
from urllib.parse import urlencode
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

#from django.contrib.auth.models import User
# Create your views here.

#@login_required(login_url='/accounts/login/')
@login_required
def index(request):
    books = Books.objects.all()
    return render(request, 'backend/index.html', {'books': books})

def handle_uploaded_file(f):
    with open('books/static/images/' + f.name, 'wb+')as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required
def create(request):
    if request.method == "POST":
        handle_uploaded_file(request.FILES['photo'])
        try:
            borrowStatus = request.POST.get('borrowStatus', '') == 'on'
            book = Books(title=request.POST['title'], author=request.POST['author'], publisher=request.POST['publisher'], photo=request.FILES['photo'], summary=request.POST['summary'],  releaseDate=request.POST['releaseDate'], borrowStatus=borrowStatus)
            book.save()
            # return HttpResponse('success')
            return HttpResponseRedirect('/backend/')
        except:
            return HttpResponse('fail')
    else:
        # return HttpResponse('success2')
        return render(request, 'backend/create.html')

@login_required
def edit(request, id):
    book = Books.objects.get(id=id)
    print(book.borrowStatus)
    return render(request, 'backend/edit.html', {'book': book})

@login_required
def update(request, id):
    if request.method == "POST":
        book = Books.objects.get(id=id)
        handle_uploaded_file(request.FILES['photo'])
        book.title = request.POST['title']
        book.author = request.POST['author']
        book.photo = request.FILES['photo']
        book.summary = request.POST['summary']
        book.releaseDate = request.POST['releaseDate']
        book.borrowStatus = request.POST.get('borrowStatus', '') == 'on'
        book.save()
        #if (request.POST.get('borrowStatus', '') == 'on'):
          #  books_loan = BorrowBooks(active=False)
        return HttpResponseRedirect("/backend/")
    else:
        book = Books.objects.get(id=id)
        return render(request, 'backend/edit.html', {'book', book})


# def pd_update(request, id):
#     book = Books.objects.get(id=id)
#     form = BooksForm(request.POST, instance=book)
#     if form.is_valid():
#         form.save()
#         return HttpResponseRedirect("/backend")
#     return render(request, 'backend/edit_pd.html', {'book', book})

@login_required
def delete(request, id):
    book = Books.objects.get(id=id)
    book.delete()
    messages.success(request, book.title + " is successfully deleted.")
    return HttpResponseRedirect("/backend/")


def show_books(request):
    count = 0
    for rec in request.session.items():
        count += 1
    books = Books.objects.all()
    context = {'books': books, 'counts': count}
    return render(request, 'frontend/index.html', context)


class BooksItems(object):
    def __init__(self, id, title, author, publisher, photo, summary, releaseDate, borrowStatus, borrowDate, dueDate):
        self.id = id
        self.title = title
        self.author = author
        self.publisher = publisher
        self.photo = photo
        self.summary = summary
        self.releaseDate = releaseDate
        self.borrowStatus = borrowStatus
        self.borrowDate = borrowDate
        self.dueDate = dueDate
    def serialize(self):
        return self.__dict__

@login_required
def add(request, id):
    #request.session.flush()
    count = 0;
    book = Books.objects.get(id=id)
    borrowStatus = True
    found = False
    #borrowDate = timezone.now()
    #dueDate = timezone.now() + timedelta(days=7)
    releaseDate = json.dumps(book.releaseDate, default=myconverter)
    borrowDate = json.dumps(timezone.now(), default=myconverter)
    dueDate = json.dumps(timezone.now() + timedelta(days=7), default=myconverter)


    #print(request.session.items())
    if 'books' in request.session.keys():
        for item in request.session['books']:
            if item['id'] == str(id):
                messages.warning(request,'Book title: ' +  book.title + " is already added.")
                found = True
                break
        if found == False:
            book_list = request.session['books']
            books = BooksItems(str(book.id), book.title, book.author, book.publisher, book.summary, str(book.photo), borrowDate, borrowStatus, borrowDate, borrowDate ).serialize()
            book_list.append(books)
            request.session['books'] = book_list
    else:
        books = []
        books.append(BooksItems(str(book.id), book.title, book.author, book.publisher, book.summary, str(book.photo), borrowDate, borrowStatus, borrowDate, borrowDate ).serialize())
        request.session['books'] = books

    #request.session['books'] = books
    for rec in request.session['books']:
        count += 1
        #print("rec-----------------------")
        #print(rec)
    #print(request.session.items())
    books = Books.objects.all()
    return render(request, 'frontend/index.html', {'books': books, 'counts': count})

def myconverter(o):
    if isinstance(o, (datetime, date)):
        return o.__str__()

@login_required
def borrow_book(request):
    for item in request.session['books']:
        id = item['id']
        book = Books.objects.get(id=id)

        book.borrowStatus = True
        book.save()

        borrowDate = timezone.now()
        dueDate = timezone.now() + timedelta(days=7)
        books_loan = BorrowBooks(borrowDate=borrowDate, dueDate=dueDate, active=True)
        books_loan.borrowBy = request.user
        print(request.user)
        books_loan.book = Books.objects.get(id=id)
        # books_loan.book = BooksLoan.objects.select_related().filter(id=id).order_by()
        books_loan.save()
    del request.session['books']

    books = Books.objects.all()
    return render(request, 'frontend/index.html', {'books': books, 'counts': 0})

@login_required
def checkout(request):
    #request.session.flush()
    count2 = 0
    if 'books' in request.session.keys():
        for rec in request.session['books']:
            count2 += 1
        books = request.session['books']
    else:
        books = []
    # print('books------------')
    # print(books)
    #for item in books:
        #print('item-------------')
        # print(item['id'])
        # print(item['title'])
        # print(item.get('author'))
        # for key, values in item.items():
        #     print('values------------')
        #     if key == 'id':
        #         print(values)
        #     if key == 'author':
        #         print(values)
            #for v in values.items():
                #print('v---------------')
                #print(v)

    #result_list = [str(v) for k,v in item.items()]
    #print(result_list[2])
    #print(books)
    context = {'books': books, 'counts': count2}
    return render(request, 'frontend/checkout.html', context)

@login_required
def removeall(request):

    del request.session['books']
    books = Books.objects.all()
    return render(request, 'frontend/index.html', {'books': books, 'counts': 0})

@login_required
def remove_me(request, id):
    found = False
    count2 = 0
    for index, item in enumerate(request.session['books']):
        #print(item['id'])
        if item['id'] == str(id):
            request.session['books'].pop(int(index))
            request.session.modified = True
            found = True
            break
    #request.session['books'].pop(0)
    #request.session.modified = True
    #print( request.session['books'])
    if found == True:
        # print(request.session.items())
        for rec in request.session['books']:
            count2 += 1
        books = request.session['books']
        context = {'books': books, 'counts': count2}
        return render(request, 'frontend/checkout.html', context)
    else:
        return HttpResponse("fail")


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    '''
    Splits the query string in invidual keywords, getting rid of unecessary spaces and grouping quoted words together.
    Example:
    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''

    return [normspace('', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    '''
    Returns a query, that is a combination of Q objects.
    That combination aims to search keywords within a model by testing the given search fields.
    '''

    query = None  ## Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  ## Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

#@login_required
def search_frontend(request):
    query_string = ''
    books = None
    count = 0
    if request.method == 'GET':
        if ('search' in request.GET) and request.GET['search'].strip():
            query_string = request.GET['search']
            entry_query = get_query(query_string, ['title', 'author', 'publisher'])
            books = Books.objects.filter(entry_query).order_by('title')
        else:
            books = Books.objects.all()
    if 'books' in request.session.keys():
        for rec in request.session['books']:
            count += 1
    context = {'books': books, 'counts': count, 'search': query_string}
    return render(request, 'frontend/index.html', context)


def search_backend(request):
    query_string = ''
    books = None
    count = 0
    if request.method == 'GET':
        if ('search' in request.GET) and request.GET['search'].strip():
            query_string = request.GET['search']
            entry_query = get_query(query_string, ['title', 'author', 'publisher'])
            books = Books.objects.filter(entry_query).order_by('title')
        else:
            books = Books.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(books, 3)
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    #return render(request, 'backend/index.html', {'books': books})
    context = {'books': books, 'search': query_string}
    return render(request, 'backend/index.html', context)


@login_required
def booklist(request):
    books = Books.objects.all()
    print(books)
    return render(request, 'backend/index.html', {'books': books})