from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm, ItemCreationForm, SupplierCreationForm
from .models import Item, Supplier, User


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
    form = ItemCreationForm

class SupplierAdmin(admin.ModelAdmin):
    form = SupplierCreationForm

admin.site.register(User, CustomUserAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Supplier, SupplierAdmin)


