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
from .controllers import UserController, FridgeContentController

'''Auth function'''
@api_view(['POST'])
def login(request):
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse(status=status.HTTP_200_OK)
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def logout(request):
    logout(request)
    return HttpResponse(status=status.HTTP_200_OK)


'''User endpoint functions'''
#Get all users who are not admins
@api_view(['GET'])
def allUsers(request):
    return UserController.getAllUsers()

@api_view(['GET', 'PUT'])
def singleUser(request, pk):
    error = UserController.singleUserCheck(pk)
    if error is None:
        # Return user model
        if request.method == 'GET':
            return UserController.getSingleUser(pk)
        # Update included fields
        if request.method == 'PUT':
            return ?UserController.updateSingleUser(request,pk)
    return error

'''Fridge Content functions'''

@api_view(['GET'])
def allFridgeContent(request):
    return FridgeContentController.getAllFridgeContent()
