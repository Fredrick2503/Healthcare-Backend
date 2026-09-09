from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from authentication.models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'name', 'email', 'is_staff', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password', 'is_staff', 'is_active'),
        }),
    )
