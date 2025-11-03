from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Product, ActiveSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'role', 'deposit', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Vending Machine', {'fields': ('role', 'deposit')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'cost', 'amount_available', 'seller', 'created_at']
    list_filter = ['seller', 'created_at']
    search_fields = ['product_name', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('product_name', 'cost', 'amount_available')}),
        ('Seller Info', {'fields': ('seller',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'token_preview']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['token', 'created_at']
    ordering = ['-created_at']
    
    def token_preview(self, obj):
        return f"{obj.token[:20]}..." if len(obj.token) > 20 else obj.token
    token_preview.short_description = 'Token Preview'