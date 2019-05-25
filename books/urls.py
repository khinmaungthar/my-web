from . import views
from django.urls import path


urlpatterns=[
    path('backend/admin', views.booklist),
    path('backend/', views.booklist),
    path('backend/create', views.create),
    path('backend/edit/<int:id>', views.edit),
    path('backend/update/<int:id>', views.update),
    path('backend/delete/<int:id>', views.delete),
    path('', views.search_frontend),
    path('frontend/', views.search_frontend),
    path('frontend/checkout/', views.checkout),
    path('frontend/add-to-cart/<int:id>', views.add),
    path('frontend/removeall/', views.removeall),
    path('frontend/borrow', views.borrow_book),
    path('frontend/remove/<int:id>', views.remove_me),
    #path('accounts/', include('django.contrib.auth.urls')),
    #path('frontend/search', views.search),
]