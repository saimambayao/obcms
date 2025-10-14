"""
OCM Admin

Django admin configuration for OCM models.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import OCMAccess


@admin.register(OCMAccess)
class OCMAccessAdmin(admin.ModelAdmin):
    """Admin interface for OCMAccess model"""
    
    list_display = [
        'user',
        'access_level_badge',
        'is_active_badge',
        'granted_at',
        'granted_by',
        'last_accessed',
    ]
    
    list_filter = [
        'is_active',
        'access_level',
        'granted_at',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'notes',
    ]
    
    readonly_fields = [
        'granted_at',
        'last_accessed',
    ]
    
    autocomplete_fields = ['user', 'granted_by']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_active', 'access_level')
        }),
        ('Grant Information', {
            'fields': ('granted_at', 'granted_by', 'last_accessed')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('user', 'granted_by')
    
    def save_model(self, request, obj, form, change):
        """Auto-set granted_by on creation"""
        if not change:  # Only on creation
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)
    
    def access_level_badge(self, obj):
        """Display access level with color-coded badge"""
        colors = {
            'viewer': '#6b7280',  # gray
            'analyst': '#3b82f6',  # blue
            'executive': '#10b981',  # emerald
        }
        color = colors.get(obj.access_level, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_access_level_display().upper()
        )
    
    access_level_badge.short_description = 'Access Level'
    
    def is_active_badge(self, obj):
        """Display active status with color-coded badge"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: 600;">ACTIVE</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ef4444; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px; font-weight: 600;">INACTIVE</span>'
            )
    
    is_active_badge.short_description = 'Status'
