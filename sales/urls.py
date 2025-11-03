from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('logout/all/', views.logout_all, name='logout_all'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('deposit/', views.deposit, name='deposit'),
    path('logout/force/', views.force_logout_all, name='force_logout_all'),
    path('buy/', views.buy, name='buy'),
    path('reset/', views.reset, name='reset'),
    path('balance/', views.balance, name='balance'),
]