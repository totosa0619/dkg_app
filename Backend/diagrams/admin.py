from django.contrib import admin
from django.contrib.auth.models import Permission
from diagrams import models


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type')
    list_filter = ('content_type',)
    search_fields = ['name', 'codename']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('content_type')


@admin.register(models.DiagramFrame)
class DiagramFrameAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'source', 'diagram_type')
    list_display_links = ('title',)


@admin.register(models.RawDataBlock)
class RawDataBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'source_name', 'active', 'dt_created', 'dt_updated')
    list_display_links = ('slug',)


@admin.register(models.PlatformAccess)
class PlatformAccessAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'access_level', 'status', 'created')
    list_display_links = ('user',)
    search_fields = ('user__email', )
    
    
@admin.register(models.DeployedDashboards)
class DeployedDashboardsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'domain', 'panel_url')
    list_display_links = ('user',)
    search_fields = ('user__username', 'domain', 'panel_url')
    
    
@admin.register(models.DiagramLogs)
class DiagramLogsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'diagram', 'path', 'dt_created')
    list_display_links = ('user', 'diagram')
    search_fields = ('user__username', 'diagram__title')


@admin.register(models.ITToolProduct)
class ITToolProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'created_at', 'updated_at']
    search_fields = ['title', 'category__name', 'user__username']
    list_filter = ['category', 'created_at']

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']