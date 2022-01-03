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
        users = User.objects.all().exclude(is_superuser=True)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    def singleUserCheck(pk):
        # Check to see if user exists
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
        # Check to see if user is admin i.e. superuser
        if user.is_superuser == True:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN) # Return 403
        return None

    def getSingleUser(pk):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

    def updateSingleUser(request,pk):
        serializer = UserSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FridgeContentController():
    def getAllFridgeContent():
        fridge_contents = FridgeContent.objects.all()
        serializer = FridgeContentSerializer(fridge_contents, many=True)
        return Response(serializer.data)

    # Checks if 
    def singleFridgeContentCreateCheck(pk): 
        # Check to see if fridge content exists
        try:
            content = FridgeContent.objects.get(id=pk)
        except FridgeContent.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
        return None


class ItemController():
    def getItemFromBarcode(barcode):
        try:
            item = Item.objects.get(barcode=barcode)
            serializer = ItemSerializer(item, many=False)
            return Response(serializer.data)
        except Item.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    
    def createItem(request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
