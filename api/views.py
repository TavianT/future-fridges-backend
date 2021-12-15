from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User

#Get all users who are not admins
@api_view(['GET'])
def allUsers(request):
    users = User.objects.all().exclude(is_superuser=True)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT'])
def singleUser(request, pk):
    # Check to see if user exists
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
    
    # Check to see if user is admin i.e. superuser
    if user.is_superuser == True:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN) # Return 403

    # Return user model
    if request.method == 'GET':
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    # Update included fields
    if request.method == 'PUT':
        serializer = UserSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
