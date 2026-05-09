from django.contrib import admin
from .models import SparesCategory, Supplier, Warehouse, Rack, Bin


@admin.register(SparesCategory)
class SparesCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'phone', 'gstin', 'gst_category', 'is_active']
    search_fields = ['supplier_name', 'gstin']
    list_filter = ['is_active', 'gst_category']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'warehouse_type', 'is_group', 'is_rejected', 'is_active']
    list_filter = ['warehouse_type', 'is_active']


@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = ['name', 'warehouse']
    list_filter = ['warehouse']


@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ['name', 'rack']
    list_filter = ['rack']