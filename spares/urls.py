from django.urls import path
from . import views

app_name = 'spares'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Masters
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),

    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/', views.warehouse_detail, name='warehouse_detail'),

    path('racks/', views.rack_list, name='rack_list'),
    path('racks/create/', views.rack_create, name='rack_create'),

    path('bins/', views.bin_list, name='bin_list'),
    path('bins/create/', views.bin_create, name='bin_create'),

    # Items
    path('items/', views.item_list, name='item_list'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),

    # Procurement
    path('quotes/', views.quote_list, name='quote_list'),
    path('quotes/create/', views.quote_create, name='quote_create'),
    path('quotes/<int:pk>/', views.quote_detail, name='quote_detail'),

    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),

    # Counter Sale
    path('counter-sales/', views.counter_sale_list, name='counter_sale_list'),
    path('counter-sales/create/', views.counter_sale_create, name='counter_sale_create'),
    path('counter-sales/<int:pk>/', views.counter_sale_detail, name='counter_sale_detail'),

    path('counter-returns/', views.counter_return_list, name='counter_return_list'),
    path('counter-returns/create/', views.counter_return_create, name='counter_return_create'),
    path('counter-returns/<int:pk>/', views.counter_return_detail, name='counter_return_detail'),

    # Issue Alteration
    path('issue-alterations/', views.issue_alteration_list, name='issue_alteration_list'),
    path('issue-alterations/create/', views.issue_alteration_create, name='issue_alteration_create'),
    path('issue-alterations/<int:pk>/', views.issue_alteration_detail, name='issue_alteration_detail'),

    # Reports
    path('stock/', views.stock_report, name='stock_report'),

    # AJAX
    path('ajax/item/<int:pk>/', views.ajax_item_details, name='ajax_item_details'),
    path('ajax/rack/<int:rack_id>/bins/', views.ajax_rack_bins, name='ajax_rack_bins'),
    path('ajax/supplier/<int:pk>/', views.ajax_supplier_details, name='ajax_supplier_details'),
    path('ajax/po/<int:po_id>/items/', views.ajax_po_items, name='ajax_po_items'),
]