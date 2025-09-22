from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserRole, Team

# UserRole
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name',)

# Team
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'team_lead', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    autocomplete_fields = ('team_lead',)

# User
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'username', 'role', 'team', 'status', 'is_staff', 'is_superuser', 'created_at')
    list_filter = ('status', 'role', 'team', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('role', 'team', 'status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'team', 'status'),
        }),
    )
    

