from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User,FridgeContent,Item
from .controllers import UserController, FridgeContentController, ItemController

'''Auth function'''
#Used to login to the app via the backend, user information is saved as an instace and can be accessed without needing to pass any information about the current user
@api_view(['POST'])
def login(request):
    #Takes data from form via POST request
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, username=email, password=password)
    if user is not None: #if login successful
        login(request, user)
        return HttpResponse(status=status.HTTP_200_OK) #return 200 TODO: might need to change status code
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED) #return 401
    return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Logs the user out and clears instance
@api_view(['POST'])
def logout(request):
    logout(request)
    return HttpResponse(status=status.HTTP_200_OK)


'''User endpoint functions'''
#Get all users who are not superusers (admins)
@api_view(['GET'])
def allUsers(request):
    return UserController.getAllUsers()

@api_view(['GET', 'PUT'])
def singleUser(request, pk):
    error = UserController.singleUserCheck(pk) #Checks to see if user exists and is not a superuser (admin)
    if error is None:
        # Return user model
        if request.method == 'GET':
            return UserController.getSingleUser(pk)
        # Update included fields
        if request.method == 'PUT':
            return UserController.updateSingleUser(request,pk)
    return error

'''Fridge Content functions'''

@api_view(['GET'])
#return all contents of the fridge
def allFridgeContent(request):
    return FridgeContentController.getAllFridgeContent()

@api_view(['POST'])
def singleFridgeContent(request,pk):
   # error = FridgeContentController.singleFridgeContentCreateCheck(pk) #
    #if error is None:  #commenting out for now
    if request.method == 'POST':
        return None #stub
            

'''Item functions'''
@api_view(['GET'])
def allItems(request):
    return ItemController.getAllItems()
#Get contents of item model from a barcode
@api_view(['GET'])
def singleItemFromBarcode(request):
    barcode = request.data['barcode']
    return ItemController.getItemFromBarcode(barcode)

@api_view(['GET','POST'])
def singleItem(request,pk):
    if request.method == 'POST':
        #create new item
        return ItemController.createItem(request)

