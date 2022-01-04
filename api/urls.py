from . import views
from django.urls import path
urlpatterns = [
    #User paths
    path('users/', views.allUsers, name="users"),
    path('user/<str:pk>/', views.singleUser, name="user"),
    #Auth paths
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    #Item paths
    path('items/', views.allItems, name="items"),
    path('item/<str:pk>/', views.singleItem, name='item'),
    path('item-barcode/', views.singleItemFromBarcode, name='item_from_barcode'),
    #Fridge content paths
    path('fridge-contents/', views.allFridgeContent, name='fridge_contents'),
    path('fridge-content/', views.singleFridgeContent, name='fridge_content'),
    #Report paths
    path('all-reports/', views.allReportsInfo, name='all-reports')
]