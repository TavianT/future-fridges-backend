from os import name

from api.reorder import Dates, Reorder
from . import views
from django.urls import path
import threading
urlpatterns = [
    #User paths
    path('users/', views.allUsers, name="users"),
    path('user/<str:pk>/', views.singleUser, name="user"),
    #Auth paths
    path('login/', views.userLogin, name='login'),
    path('logout/', views.userLogout, name='logout'),
    #Item paths
    path('items/', views.allItems, name="items"),
    #path('item/<str:pk>/', views.singleItem, name='item'),
    path('create-item/', views.createItem, name='create-item'),
    path('item-barcode/<str:barcode>/', views.singleItemFromBarcode, name='item-barcode'),
    #Fridge content paths
    path('fridge-contents/', views.allFridgeContent, name='fridge-contents'),
    #path('fridge-content/<str:pk>/', views.singleFridgeContent, name='fridge_content'),
    path('create-fridge-content/', views.createFridgeContent, name='create-fridge-content'),
    path('update-fridge-content-quantity/<str:pk>/', views.updateContentQuantity, name='update-quantity'),
    #Report paths
    path('all-reports/', views.allReportsInfo, name='all-reports'),
    path('generate-report/', views.generateReport, name='generate-report'),
    path('download-report/<str:filename>/', views.returnReport, name='donwload-report'),
    #Door paths
    path('unlock-door/', views.unlockDoor, name="unlock-door"),
    path('lock-door/', views.lockDoor, name="lock-door"),
    #Activity log paths
    path('logs/', views.recentActivityLogs, name='logs'),
    path('download-log/<str:filename>/', views.returnLog, name='download-log')
]

#TODO: Every monday reorder empty items
print("Checking for reorder")
t = threading.Thread(target=Reorder.run,args=[Dates.Monday], daemon=True)
t.start()