from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
import json

from .models import (
    SparesItem, ItemRackBin, StockLedger,
    SupplierQuote, SupplierQuoteItem,
    PurchaseOrder, PurchaseOrderItem,
    PurchaseInvoice, PurchaseInvoiceItem,
    CounterSale, CounterSaleItem,
    CounterSaleReturn, CounterSaleReturnItem,
    SparesIssueAlteration, SparesIssueAlterationItem, SparesIssueAlterationDeleted,
)
from .forms import (
    SparesItemForm, ItemRackBinFormSet,
    SupplierQuoteForm, SupplierQuoteItemFormSet,
    PurchaseOrderForm, PurchaseOrderItemFormSet,
    PurchaseInvoiceForm, PurchaseInvoiceItemFormSet,
    CounterSaleForm, CounterSaleItemFormSet,
    CounterSaleReturnForm, CounterSaleReturnItemFormSet,
    SparesIssueAlterationForm, SparesIssueItemFormSet, SparesIssueDeletedFormSet,
    SupplierForm, WarehouseForm, RackForm, BinForm, SparesCategoryForm,
)
from masters.models import Supplier, Warehouse, SparesCategory, Rack, Bin


# ── Dashboard ─────────────────────────────────────────────

@login_required
def dashboard(request):
    context = {
        'total_items': SparesItem.objects.filter(is_active=True).count(),
        'total_suppliers': Supplier.objects.filter(is_active=True).count(),
        'pending_orders': PurchaseOrder.objects.filter(status='submitted').count(),
        'unpaid_invoices': PurchaseInvoice.objects.filter(payment_status='Unpaid').count(),
        'recent_sales': CounterSale.objects.order_by('-date')[:5],
        'low_stock': StockLedger.objects.select_related('item', 'warehouse').filter(
            quantity__lte=models_low_stock()
        )[:10],
    }
    return render(request, 'spares/dashboard.html', context)


def models_low_stock():
    return 5


# ── AJAX Helpers ──────────────────────────────────────────

@login_required
def ajax_item_details(request, pk):
    item = get_object_or_404(SparesItem, pk=pk)
    return JsonResponse({
        'item_code': item.item_code,
        'item_name': item.item_name,
        'uom': item.uom,
        'rate': float(item.standard_selling_rate),
        'mrp': float(item.mrp),
        'sgst': float(item.sgst),
        'cgst': float(item.cgst),
    })


@login_required
def ajax_rack_bins(request, rack_id):
    bins = Bin.objects.filter(rack_id=rack_id).values('id', 'name')
    return JsonResponse({'bins': list(bins)})


@login_required
def ajax_supplier_details(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    return JsonResponse({
        'gstin': supplier.gstin,
        'gst_category': supplier.gst_category,
        'place_of_supply': supplier.place_of_supply,
    })


@login_required
def ajax_po_items(request, po_id):
    """Load purchase order items for invoice creation"""
    po = get_object_or_404(PurchaseOrder, pk=po_id)
    items = []
    for item in po.items.select_related('item', 'warehouse'):
        items.append({
            'item_id': item.item.id,
            'item_code': item.item.item_code,
            'item_name': item.item.item_name,
            'warehouse_id': item.warehouse.id,
            'quantity': float(item.quantity),
            'uom': item.uom,
            'rate': float(item.rate),
            'sgst': float(item.item.sgst),
            'cgst': float(item.item.cgst),
        })
    return JsonResponse({
        'items': items,
        'supplier_id': po.supplier.id,
        'supplier_gstin': po.supplier_gstin,
        'gst_category': po.gst_category,
        'place_of_supply': po.place_of_supply,
    })


# ── Masters: Supplier ─────────────────────────────────────

@login_required
def supplier_list(request):
    q = request.GET.get('q', '')
    suppliers = Supplier.objects.all()
    if q:
        suppliers = suppliers.filter(
            Q(supplier_name__icontains=q) | Q(gstin__icontains=q)
        )
    return render(request, 'spares/supplier_list.html', {'suppliers': suppliers, 'q': q})


@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            messages.success(request, f'Supplier {supplier.supplier_name} created.')
            return redirect('spares:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm()
    return render(request, 'spares/supplier_form.html', {'form': form, 'title': 'New Supplier'})


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated.')
            return redirect('spares:supplier_detail', pk=pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'spares/supplier_form.html', {'form': form, 'obj': supplier, 'title': 'Edit Supplier'})


# ── Masters: Warehouse ────────────────────────────────────

@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'spares/warehouse_list.html', {'warehouses': warehouses})


@login_required
def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Warehouse created.')
            return redirect('spares:warehouse_list')
    else:
        form = WarehouseForm()
    return render(request, 'spares/warehouse_form.html', {'form': form, 'title': 'New Warehouse'})


@login_required
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Warehouse updated.')
            return redirect('spares:warehouse_detail', pk=pk)
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, 'spares/warehouse_form.html', {'form': form, 'obj': warehouse, 'title': 'Edit Warehouse'})


# ── Masters: Rack & Bin ───────────────────────────────────

@login_required
def rack_list(request):
    racks = Rack.objects.select_related('warehouse').all()
    return render(request, 'spares/rack_list.html', {'racks': racks})


@login_required
def rack_create(request):
    if request.method == 'POST':
        form = RackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rack created.')
            return redirect('spares:rack_list')
    else:
        form = RackForm()
    return render(request, 'spares/rack_form.html', {'form': form, 'title': 'New Rack'})


@login_required
def bin_list(request):
    bins = Bin.objects.select_related('rack__warehouse').all()
    return render(request, 'spares/bin_list.html', {'bins': bins})


@login_required
def bin_create(request):
    if request.method == 'POST':
        form = BinForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bin created.')
            return redirect('spares:bin_list')
    else:
        form = BinForm()
    return render(request, 'spares/bin_form.html', {'form': form, 'title': 'New Bin'})


# ── Spares Item ───────────────────────────────────────────

@login_required
def item_list(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    items = SparesItem.objects.select_related('category').all()
    if q:
        items = items.filter(
            Q(item_code__icontains=q) | Q(item_name__icontains=q) | Q(part_number__icontains=q)
        )
    if category:
        items = items.filter(category_id=category)
    categories = SparesCategory.objects.all()
    return render(request, 'spares/item_list.html', {
        'items': items, 'q': q, 'categories': categories, 'selected_category': category
    })


@login_required
def item_create(request):
    if request.method == 'POST':
        form = SparesItemForm(request.POST)
        formset = ItemRackBinFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                item = form.save(commit=False)
                item.created_by = request.user
                item.save()
                formset.instance = item
                formset.save()
            messages.success(request, f'Item {item.item_code} created.')
            return redirect('spares:item_detail', pk=item.pk)
    else:
        form = SparesItemForm()
        formset = ItemRackBinFormSet()
    return render(request, 'spares/item_form.html', {
        'form': form, 'formset': formset, 'title': 'New Spares Item'
    })


@login_required
def item_detail(request, pk):
    item = get_object_or_404(SparesItem, pk=pk)
    stock = StockLedger.objects.filter(item=item).select_related('warehouse', 'rack', 'bin')
    if request.method == 'POST':
        form = SparesItemForm(request.POST, instance=item)
        formset = ItemRackBinFormSet(request.POST, instance=item)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, 'Item updated.')
            return redirect('spares:item_detail', pk=pk)
    else:
        form = SparesItemForm(instance=item)
        formset = ItemRackBinFormSet(instance=item)
    return render(request, 'spares/item_form.html', {
        'form': form, 'formset': formset, 'obj': item, 'stock': stock, 'title': 'Edit Spares Item'
    })


# ── Supplier Quote ────────────────────────────────────────

@login_required
def quote_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    quotes = SupplierQuote.objects.select_related('supplier').order_by('-date')
    if q:
        quotes = quotes.filter(
            Q(quote_no__icontains=q) | Q(supplier__supplier_name__icontains=q)
        )
    if status:
        quotes = quotes.filter(status=status)
    return render(request, 'spares/quote_list.html', {
        'quotes': quotes, 'q': q, 'status': status,
        'status_choices': SupplierQuote.STATUS,
    })


@login_required
def quote_create(request):
    if request.method == 'POST':
        form = SupplierQuoteForm(request.POST)
        formset = SupplierQuoteItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                quote = form.save(commit=False)
                quote.created_by = request.user
                quote.save()
                formset.instance = quote
                items = formset.save()
                # Recalculate totals
                _recalculate_quote_totals(quote)
            messages.success(request, f'Supplier Quote {quote.quote_no} created.')
            return redirect('spares:quote_detail', pk=quote.pk)
    else:
        form = SupplierQuoteForm(initial={'date': timezone.now().date()})
        formset = SupplierQuoteItemFormSet()
    return render(request, 'spares/quote_form.html', {
        'form': form, 'formset': formset, 'title': 'New Supplier Quote'
    })


@login_required
def quote_detail(request, pk):
    quote = get_object_or_404(SupplierQuote, pk=pk)
    if request.method == 'POST':
        form = SupplierQuoteForm(request.POST, instance=quote)
        formset = SupplierQuoteItemFormSet(request.POST, instance=quote)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                _recalculate_quote_totals(quote)
            messages.success(request, 'Quote updated.')
            return redirect('spares:quote_detail', pk=pk)
    else:
        form = SupplierQuoteForm(instance=quote)
        formset = SupplierQuoteItemFormSet(instance=quote)
    return render(request, 'spares/quote_form.html', {
        'form': form, 'formset': formset, 'obj': quote, 'title': f'Quote {quote.quote_no}'
    })


def _recalculate_quote_totals(quote):
    items = quote.items.all()
    total_qty = sum(i.quantity for i in items)
    total_amt = sum(i.amount for i in items)
    discount_amt = total_amt * quote.additional_discount_percent / 100
    grand = total_amt - discount_amt - quote.additional_discount_amount
    SupplierQuote.objects.filter(pk=quote.pk).update(
        total_quantity=total_qty,
        total_amount=total_amt,
        additional_discount_amount=discount_amt,
        grand_total=grand,
    )


# ── Purchase Order ────────────────────────────────────────

@login_required
def order_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    orders = PurchaseOrder.objects.select_related('supplier').order_by('-date')
    if q:
        orders = orders.filter(
            Q(po_no__icontains=q) | Q(supplier__supplier_name__icontains=q)
        )
    if status:
        orders = orders.filter(status=status)
    return render(request, 'spares/order_list.html', {
        'orders': orders, 'q': q, 'status': status,
        'status_choices': PurchaseOrder.STATUS,
    })


@login_required
def order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.created_by = request.user
                order.save()
                formset.instance = order
                formset.save()
                _recalculate_order_totals(order)
            messages.success(request, f'Purchase Order {order.po_no} created.')
            return redirect('spares:order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm(initial={'date': timezone.now().date()})
        formset = PurchaseOrderItemFormSet()
    return render(request, 'spares/order_form.html', {
        'form': form, 'formset': formset, 'title': 'New Purchase Order'
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        formset = PurchaseOrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                _recalculate_order_totals(order)
            messages.success(request, 'Purchase Order updated.')
            return redirect('spares:order_detail', pk=pk)
    else:
        form = PurchaseOrderForm(instance=order)
        formset = PurchaseOrderItemFormSet(instance=order)
    return render(request, 'spares/order_form.html', {
        'form': form, 'formset': formset, 'obj': order, 'title': f'PO {order.po_no}'
    })


def _recalculate_order_totals(order):
    items = order.items.all()
    total_qty = sum(i.quantity for i in items)
    total_amt = sum(i.amount for i in items)
    PurchaseOrder.objects.filter(pk=order.pk).update(
        total_quantity=total_qty,
        total_amount=total_amt,
        grand_total=total_amt,
    )


# ── Purchase Invoice ──────────────────────────────────────

@login_required
def invoice_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    payment = request.GET.get('payment', '')
    invoices = PurchaseInvoice.objects.select_related('supplier').order_by('-date')
    if q:
        invoices = invoices.filter(
            Q(invoice_no__icontains=q) | Q(supplier__supplier_name__icontains=q)
        )
    if status:
        invoices = invoices.filter(status=status)
    if payment:
        invoices = invoices.filter(payment_status=payment)
    return render(request, 'spares/invoice_list.html', {
        'invoices': invoices, 'q': q, 'status': status, 'payment': payment,
        'status_choices': PurchaseInvoice.STATUS,
    })


@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST)
        formset = PurchaseInvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.created_by = request.user
                invoice.save()
                formset.instance = invoice
                formset.save()
                _recalculate_invoice_totals(invoice)
                # Update stock ledger
                _update_stock_on_invoice(invoice, add=True)
            messages.success(request, f'Purchase Invoice {invoice.invoice_no} created.')
            return redirect('spares:invoice_detail', pk=invoice.pk)
    else:
        form = PurchaseInvoiceForm(initial={'date': timezone.now().date()})
        formset = PurchaseInvoiceItemFormSet()
    return render(request, 'spares/invoice_form.html', {
        'form': form, 'formset': formset, 'title': 'New Purchase Invoice'
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    if request.method == 'POST':
        form = PurchaseInvoiceForm(request.POST, instance=invoice)
        formset = PurchaseInvoiceItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                _recalculate_invoice_totals(invoice)
            messages.success(request, 'Invoice updated.')
            return redirect('spares:invoice_detail', pk=pk)
    else:
        form = PurchaseInvoiceForm(instance=invoice)
        formset = PurchaseInvoiceItemFormSet(instance=invoice)
    return render(request, 'spares/invoice_form.html', {
        'form': form, 'formset': formset, 'obj': invoice, 'title': f'Invoice {invoice.invoice_no}'
    })


def _recalculate_invoice_totals(invoice):
    items = invoice.items.all()
    total_qty = sum(i.quantity for i in items)
    total_amt = sum(i.amount for i in items)
    total_sgst = sum(i.sgst_amount for i in items)
    total_cgst = sum(i.cgst_amount for i in items)
    total_taxes = total_sgst + total_cgst
    grand = total_amt + total_taxes
    PurchaseInvoice.objects.filter(pk=invoice.pk).update(
        total_quantity=total_qty,
        total_amount=total_amt,
        total_sgst=total_sgst,
        total_cgst=total_cgst,
        total_taxes=total_taxes,
        grand_total=grand,
    )


def _update_stock_on_invoice(invoice, add=True):
    for item in invoice.items.all():
        ledger, _ = StockLedger.objects.get_or_create(
            item=item.item,
            warehouse=item.warehouse,
            rack=item.rack,
            bin=item.bin,
        )
        if add:
            ledger.quantity += item.quantity
        else:
            ledger.quantity -= item.quantity
        ledger.save()


# ── Counter Sale ──────────────────────────────────────────

@login_required
def counter_sale_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    sales = CounterSale.objects.order_by('-date')
    if q:
        sales = sales.filter(
            Q(sale_no__icontains=q) | Q(customer__icontains=q) | Q(mobile__icontains=q)
        )
    if status:
        sales = sales.filter(status=status)
    return render(request, 'spares/counter_sale_list.html', {
        'sales': sales, 'q': q, 'status': status,
        'status_choices': CounterSale.STATUS,
    })


@login_required
def counter_sale_create(request):
    if request.method == 'POST':
        form = CounterSaleForm(request.POST)
        formset = CounterSaleItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                sale = form.save(commit=False)
                sale.created_by = request.user
                sale.save()
                formset.instance = sale
                formset.save()
                _recalculate_sale_totals(sale)
                # Deduct stock
                _update_stock_on_sale(sale, deduct=True)
            messages.success(request, f'Counter Sale {sale.sale_no} created.')
            return redirect('spares:counter_sale_detail', pk=sale.pk)
    else:
        form = CounterSaleForm(initial={'date': timezone.now().date()})
        formset = CounterSaleItemFormSet()
    return render(request, 'spares/counter_sale_form.html', {
        'form': form, 'formset': formset, 'title': 'New Counter Sale'
    })


@login_required
def counter_sale_detail(request, pk):
    sale = get_object_or_404(CounterSale, pk=pk)
    is_readonly = sale.status == 'submitted'
    if request.method == 'POST' and not is_readonly:
        form = CounterSaleForm(request.POST, instance=sale)
        formset = CounterSaleItemFormSet(request.POST, instance=sale)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                _recalculate_sale_totals(sale)
            messages.success(request, 'Counter Sale updated.')
            return redirect('spares:counter_sale_detail', pk=pk)
    else:
        form = CounterSaleForm(instance=sale)
        formset = CounterSaleItemFormSet(instance=sale)
    return render(request, 'spares/counter_sale_form.html', {
        'form': form, 'formset': formset, 'obj': sale,
        'is_readonly': is_readonly, 'title': f'Sale {sale.sale_no}'
    })


def _recalculate_sale_totals(sale):
    items = sale.items.all()
    total_qty = sum(i.quantity for i in items)
    total_amt = sum(i.total for i in items)
    discount_amt = total_amt * sale.discount / 100
    pending = total_amt - discount_amt - sale.advance_amount
    CounterSale.objects.filter(pk=sale.pk).update(
        total_qty=total_qty,
        total_amount=total_amt,
        discount_amount=discount_amt,
        pending_amount=max(pending, 0),
        payment_status='Paid' if pending <= 0 else 'Unpaid',
    )


def _update_stock_on_sale(sale, deduct=True):
    for item in sale.items.all():
        try:
            ledger = StockLedger.objects.get(
                item=item.item,
                warehouse=sale.godown,
                rack=item.rack,
                bin=item.bin,
            )
            if deduct:
                ledger.quantity -= item.quantity
            else:
                ledger.quantity += item.quantity
            ledger.save()
        except StockLedger.DoesNotExist:
            pass


# ── Counter Sale Return ───────────────────────────────────

@login_required
def counter_return_list(request):
    returns = CounterSaleReturn.objects.select_related('original_sale').order_by('-return_date')
    return render(request, 'spares/counter_return_list.html', {'returns': returns})


@login_required
def counter_return_create(request):
    sale_id = request.GET.get('sale_id')
    initial = {}
    if sale_id:
        initial['original_sale'] = sale_id
    if request.method == 'POST':
        form = CounterSaleReturnForm(request.POST)
        formset = CounterSaleReturnItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                ret = form.save(commit=False)
                ret.created_by = request.user
                ret.save()
                formset.instance = ret
                items = formset.save()
                total = sum(i.amount for i in ret.items.all())
                CounterSaleReturn.objects.filter(pk=ret.pk).update(total_amount=total)
                # Return stock
                _update_stock_on_return(ret)
            messages.success(request, f'Return {ret.return_no} created.')
            return redirect('spares:counter_return_detail', pk=ret.pk)
    else:
        form = CounterSaleReturnForm(
            initial={**initial, 'return_date': timezone.now().date()}
        )
        formset = CounterSaleReturnItemFormSet()
    return render(request, 'spares/counter_return_form.html', {
        'form': form, 'formset': formset, 'title': 'New Counter Sale Return'
    })


@login_required
def counter_return_detail(request, pk):
    ret = get_object_or_404(CounterSaleReturn, pk=pk)
    return render(request, 'spares/counter_return_form.html', {
        'obj': ret, 'is_readonly': True, 'title': f'Return {ret.return_no}'
    })


def _update_stock_on_return(ret):
    original_sale = ret.original_sale
    for item in ret.items.all():
        ledger, _ = StockLedger.objects.get_or_create(
            item=item.item,
            warehouse=original_sale.godown,
            rack=None,
            bin=None,
        )
        ledger.quantity += item.quantity
        ledger.save()


# ── Spares Issue Alteration ───────────────────────────────

@login_required
def issue_alteration_list(request):
    q = request.GET.get('q', '')
    issues = SparesIssueAlteration.objects.select_related('godown').order_by('-date')
    if q:
        issues = issues.filter(
            Q(job_card__icontains=q) | Q(godown__name__icontains=q)
        )
    return render(request, 'spares/issue_alteration_list.html', {'issues': issues, 'q': q})


@login_required
def issue_alteration_create(request):
    if request.method == 'POST':
        form = SparesIssueAlterationForm(request.POST)
        item_formset = SparesIssueItemFormSet(request.POST, prefix='items')
        deleted_formset = SparesIssueDeletedFormSet(request.POST, prefix='deleted')
        if form.is_valid() and item_formset.is_valid() and deleted_formset.is_valid():
            with transaction.atomic():
                issue = form.save(commit=False)
                issue.created_by = request.user
                issue.save()
                item_formset.instance = issue
                deleted_formset.instance = issue
                item_formset.save()
                deleted_formset.save()
                _recalculate_issue_totals(issue)
            messages.success(request, f'Spares Issue Alteration created.')
            return redirect('spares:issue_alteration_detail', pk=issue.pk)
    else:
        form = SparesIssueAlterationForm(initial={'date': timezone.now().date()})
        item_formset = SparesIssueItemFormSet(prefix='items')
        deleted_formset = SparesIssueDeletedFormSet(prefix='deleted')
    return render(request, 'spares/issue_alteration_form.html', {
        'form': form,
        'item_formset': item_formset,
        'deleted_formset': deleted_formset,
        'title': 'New Spares Issue Alteration',
    })


@login_required
def issue_alteration_detail(request, pk):
    issue = get_object_or_404(SparesIssueAlteration, pk=pk)
    if request.method == 'POST':
        form = SparesIssueAlterationForm(request.POST, instance=issue)
        item_formset = SparesIssueItemFormSet(request.POST, instance=issue, prefix='items')
        deleted_formset = SparesIssueDeletedFormSet(request.POST, instance=issue, prefix='deleted')
        if form.is_valid() and item_formset.is_valid() and deleted_formset.is_valid():
            with transaction.atomic():
                form.save()
                item_formset.save()
                deleted_formset.save()
                _recalculate_issue_totals(issue)
            messages.success(request, 'Updated.')
            return redirect('spares:issue_alteration_detail', pk=pk)
    else:
        form = SparesIssueAlterationForm(instance=issue)
        item_formset = SparesIssueItemFormSet(instance=issue, prefix='items')
        deleted_formset = SparesIssueDeletedFormSet(instance=issue, prefix='deleted')
    return render(request, 'spares/issue_alteration_form.html', {
        'form': form,
        'item_formset': item_formset,
        'deleted_formset': deleted_formset,
        'obj': issue,
        'title': f'Issue Alteration #{issue.pk}',
    })


def _recalculate_issue_totals(issue):
    items = issue.items.all()
    spares_total = sum(i.total for i in items)
    updated = spares_total + issue.labour_total + issue.outwork_total
    discount_amt = updated * issue.discount / 100 if issue.discount else 0
    SparesIssueAlteration.objects.filter(pk=issue.pk).update(
        spares_total=spares_total,
        total=updated,
        updated_total=updated - discount_amt,
    )


# ── Stock Report ──────────────────────────────────────────

@login_required
def stock_report(request):
    warehouse_id = request.GET.get('warehouse', '')
    item_q = request.GET.get('item', '')
    stock = StockLedger.objects.select_related('item', 'warehouse', 'rack', 'bin')
    if warehouse_id:
        stock = stock.filter(warehouse_id=warehouse_id)
    if item_q:
        stock = stock.filter(
            Q(item__item_code__icontains=item_q) | Q(item__item_name__icontains=item_q)
        )
    warehouses = Warehouse.objects.filter(is_active=True)
    return render(request, 'spares/stock_report.html', {
        'stock': stock,
        'warehouses': warehouses,
        'warehouse_id': warehouse_id,
        'item_q': item_q,
    })