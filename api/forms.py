from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm, fields
from .models import Order, OrderItem, Supplier, User, Item

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)

class ItemCreationForm(ModelForm):

    class Meta:
        model = Item
        fields = '__all__'

class SupplierCreationForm(ModelForm):

    class Meta:
        model = Supplier
        fields = '__all__'

class OrderItemCreationForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderCreationForm(ModelForm):
    class Meta:
        model = Order
        fields = ['order_items', 'delivery_driver']