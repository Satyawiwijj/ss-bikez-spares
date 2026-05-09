from django.contrib import admin
from .models import (
    SparesItem, StockLedger,
    SupplierQuote, SupplierQuoteItem,
    PurchaseOrder, PurchaseOrderItem,
    PurchaseInvoice, PurchaseInvoiceItem,
    CounterSale, CounterSaleItem,
    CounterSaleReturn, CounterSaleReturnItem,
    SparesIssueAlteration, SparesIssueAlterationItem, SparesIssueAlterationDeleted
)


class SupplierQuoteItemInline(admin.TabularInline):
    model = SupplierQuoteItem
    extra = 1


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


class PurchaseInvoiceItemInline(admin.TabularInline):
    model = PurchaseInvoiceItem
    extra = 1


class CounterSaleItemInline(admin.TabularInline):
    model = CounterSaleItem
    extra = 1


class CounterSaleReturnItemInline(admin.TabularInline):
    model = CounterSaleReturnItem
    extra = 1


class SparesIssueItemInline(admin.TabularInline):
    model = SparesIssueAlterationItem
    extra = 1


class SparesIssueDeletedInline(admin.TabularInline):
    model = SparesIssueAlterationDeleted
    extra = 1


@admin.register(SparesItem)
class SparesItemAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'item_name', 'category', 'mrp', 'standard_selling_rate', 'is_active']
    search_fields = ['item_code', 'item_name']
    list_filter = ['category', 'is_active']


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = ['item', 'warehouse', 'rack', 'bin', 'quantity']


@admin.register(SupplierQuote)
class SupplierQuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_no', 'supplier', 'date', 'status', 'grand_total']
    inlines = [SupplierQuoteItemInline]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_no', 'supplier', 'date', 'status', 'grand_total']
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_no', 'supplier', 'date', 'status', 'grand_total', 'payment_status']
    inlines = [PurchaseInvoiceItemInline]


@admin.register(CounterSale)
class CounterSaleAdmin(admin.ModelAdmin):
    list_display = ['sale_no', 'customer', 'date', 'total_amount', 'payment_status']
    inlines = [CounterSaleItemInline]


@admin.register(CounterSaleReturn)
class CounterSaleReturnAdmin(admin.ModelAdmin):
    list_display = ['return_no', 'original_sale', 'return_date', 'total_amount']
    inlines = [CounterSaleReturnItemInline]


@admin.register(SparesIssueAlteration)
class SparesIssueAlterationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'job_card', 'date', 'total', 'updated_total']
    inlines = [SparesIssueItemInline, SparesIssueDeletedInline]