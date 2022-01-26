from django.db.models import fields
from rest_framework import serializers
from .models import Door, Notification, User, Item, FridgeContent

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'fridge_access']
        read_only_fields = ['id', 'email', 'name']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class FridgeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FridgeContent
        fields = '__all__'

class DoorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Door
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
