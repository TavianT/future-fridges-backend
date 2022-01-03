from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework import serializers
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer,FridgeContentSerializer,ItemSerializer
from .models import User,FridgeContent,Item

class UserController():
    def getAllUsers():
        users = User.objects.all().exclude(is_superuser=True) #exclude superusers (admins) in from the query
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    def singleUserCheck(pk):
        # Check to see if user exists
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist: #check if the user exists
            return HttpResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
        # Check to see if user is admin i.e. superuser
        if user.is_superuser == True:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN) # Return 403
        return None

    #get a single user from a primary key
    def getSingleUser(pk):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

    #update a single user with primary key pk with the contents of requests
    def updateSingleUser(request,pk):
        serializer = UserSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FridgeContentController():
    #returns all fridge content
    def getAllFridgeContent():
        fridge_contents = FridgeContent.objects.all()
        serializer = FridgeContentSerializer(fridge_contents, many=True)
        return Response(serializer.data)

    # Check to see if fridge content exists
    def singleFridgeContentCreateCheck(pk): 
        try:
            content = FridgeContent.objects.get(id=pk)
        except FridgeContent.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
        return None


class ItemController():
    #get all items
    def getAllItems():
        items = Item.objects.all()
        serializer = FridgeContentSerializer(items, many=True)
        return Response(serializer.data)
    #get item from barcode
    def getItemFromBarcode(barcode):
        try:
            item = Item.objects.get(barcode=barcode)
            serializer = ItemSerializer(item, many=False)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    #create item from request
    def createItem(request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
