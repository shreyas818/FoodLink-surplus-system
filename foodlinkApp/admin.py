from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import FoodDonation, CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(FoodDonation)
admin.site.register(CustomUser, CustomUserAdmin)
