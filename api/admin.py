from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm, ItemCreationForm, OrderCreationForm, OrderItemCreationForm, SupplierCreationForm
from .models import Item, Order, OrderItem, Supplier, User


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'role')
    list_filter = ('email', 'role', 'fridge_access')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        ('Permissions', {'fields': ('role', 'fridge_access')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'role', 'fridge_access')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id','name','barcode', 'supplier')
    search_fields = ('name','barcode')
    list_filter = ('supplier',)
    form = ItemCreationForm

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'contact_number')
    search_fields = ('name','email')
    form = SupplierCreationForm

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'items', 'delivered')
    search_fields = ('items',)
    list_filter = ('delivered',)
    form = OrderCreationForm

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'quantity')
    form = OrderItemCreationForm

admin.site.register(User, CustomUserAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)


