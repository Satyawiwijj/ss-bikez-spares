from django import forms
from django.forms import inlineformset_factory
from .models import (
    SparesItem, ItemRackBin,
    SupplierQuote, SupplierQuoteItem,
    PurchaseOrder, PurchaseOrderItem,
    PurchaseInvoice, PurchaseInvoiceItem,
    CounterSale, CounterSaleItem,
    CounterSaleReturn, CounterSaleReturnItem,
    SparesIssueAlteration, SparesIssueAlterationItem, SparesIssueAlterationDeleted,
)
from masters.models import Supplier, Warehouse, SparesCategory, Rack, Bin


# ── Masters Forms ─────────────────────────────────────────

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ['created_at', 'updated_at', 'created_by']
        widgets = {
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'gstin': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_category': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'place_of_supply': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        exclude = ['created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse_type': forms.Select(attrs={'class': 'form-select'}),
            'parent_warehouse': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pin': forms.TextInput(attrs={'class': 'form-control'}),
            'is_group': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_rejected': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RackForm(forms.ModelForm):
    class Meta:
        model = Rack
        exclude = ['created_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
        }


class BinForm(forms.ModelForm):
    class Meta:
        model = Bin
        exclude = ['created_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rack': forms.Select(attrs={'class': 'form-select'}),
        }


class SparesCategoryForm(forms.ModelForm):
    class Meta:
        model = SparesCategory
        exclude = ['created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ── Spares Item Form ──────────────────────────────────────

class SparesItemForm(forms.ModelForm):
    class Meta:
        model = SparesItem
        exclude = ['item_code', 'created_at', 'updated_at', 'created_by']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'item_sub_group': forms.TextInput(attrs={'class': 'form-control'}),
            'hsn_sac': forms.TextInput(attrs={'class': 'form-control'}),
            'uom': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'opening_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'valuation_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'standard_selling_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sgst': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cgst': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'reorder_qty': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'warranty_period_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'maintain_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_negative_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_ineligible_for_itc': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


ItemRackBinFormSet = inlineformset_factory(
    SparesItem, ItemRackBin,
    fields=['rack', 'bin', 'is_active'],
    extra=1,
    can_delete=True,
    widgets={
        'rack': forms.Select(attrs={'class': 'form-select rack-select'}),
        'bin': forms.Select(attrs={'class': 'form-select bin-select'}),
        'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)


# ── Supplier Quote Forms ──────────────────────────────────

class SupplierQuoteForm(forms.ModelForm):
    class Meta:
        model = SupplierQuote
        exclude = ['quote_no', 'total_quantity', 'total_amount', 'grand_total', 'created_at', 'updated_at', 'created_by']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_till': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quotation_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'additional_discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'additional_discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_reverse_charge': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SupplierQuoteItemForm(forms.ModelForm):
    class Meta:
        model = SupplierQuoteItem
        exclude = ['amount']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'required_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control qty-input', 'step': '0.001'}),
            'uom': forms.TextInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control rate-input', 'step': '0.01'}),
        }


SupplierQuoteItemFormSet = inlineformset_factory(
    SupplierQuote, SupplierQuoteItem,
    form=SupplierQuoteItemForm,
    extra=1,
    can_delete=True,
)


# ── Purchase Order Forms ──────────────────────────────────

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        exclude = ['po_no', 'supplier_name', 'total_quantity', 'total_amount', 'total_taxes', 'grand_total', 'created_at', 'updated_at', 'created_by']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select supplier-select'}),
            'supplier_quote': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'required_by': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'supplier_gstin': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_category': forms.TextInput(attrs={'class': 'form-control'}),
            'place_of_supply': forms.TextInput(attrs={'class': 'form-control'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_reverse_charge': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_subcontracted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        exclude = ['amount', 'received_qty']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'required_by': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control qty-input', 'step': '0.001'}),
            'uom': forms.TextInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control rate-input', 'step': '0.01'}),
        }


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder, PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
)


# ── Purchase Invoice Forms ────────────────────────────────

class PurchaseInvoiceForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoice
        exclude = ['invoice_no', 'total_quantity', 'total_amount', 'total_sgst', 'total_cgst', 'total_taxes', 'grand_total', 'payment_status', 'created_at', 'updated_at', 'created_by']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select supplier-select'}),
            'purchase_order': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'supplier_gstin': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_category': forms.TextInput(attrs={'class': 'form-control'}),
            'place_of_supply': forms.TextInput(attrs={'class': 'form-control'}),
            'transporter': forms.TextInput(attrs={'class': 'form-control'}),
            'mode_of_transport': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.TextInput(attrs={'class': 'form-control'}),
            'transport_receipt_no': forms.TextInput(attrs={'class': 'form-control'}),
            'transport_receipt_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vehicle_no': forms.TextInput(attrs={'class': 'form-control'}),
            'distance_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gst_transporter_id': forms.TextInput(attrs={'class': 'form-control'}),
            'itc_classification': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hold_invoice': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_reverse_charge': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_subcontracted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PurchaseInvoiceItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseInvoiceItem
        exclude = ['amount', 'sgst_amount', 'cgst_amount', 'total']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'rack': forms.Select(attrs={'class': 'form-select rack-select'}),
            'bin': forms.Select(attrs={'class': 'form-select bin-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control qty-input', 'step': '0.001'}),
            'uom': forms.TextInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control rate-input', 'step': '0.01'}),
            'sgst': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cgst': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


PurchaseInvoiceItemFormSet = inlineformset_factory(
    PurchaseInvoice, PurchaseInvoiceItem,
    form=PurchaseInvoiceItemForm,
    extra=1,
    can_delete=True,
)


# ── Counter Sale Forms ────────────────────────────────────

class CounterSaleForm(forms.ModelForm):
    class Meta:
        model = CounterSale
        exclude = ['sale_no', 'total_qty', 'discount_amount', 'total_amount', 'pending_amount', 'payment_status', 'created_at', 'updated_at', 'created_by']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_category': forms.TextInput(attrs={'class': 'form-control'}),
            'godown': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'advance_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'pay_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'spot_sale': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_warranty': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CounterSaleItemForm(forms.ModelForm):
    class Meta:
        model = CounterSaleItem
        exclude = ['amount', 'total']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'rack': forms.Select(attrs={'class': 'form-select rack-select'}),
            'bin': forms.Select(attrs={'class': 'form-select bin-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control qty-input', 'step': '0.001'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control rate-input', 'step': '0.01'}),
            'gst_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


CounterSaleItemFormSet = inlineformset_factory(
    CounterSale, CounterSaleItem,
    form=CounterSaleItemForm,
    extra=1,
    can_delete=True,
)


# ── Counter Sale Return Forms ─────────────────────────────

class CounterSaleReturnForm(forms.ModelForm):
    class Meta:
        model = CounterSaleReturn
        exclude = ['return_no', 'total_amount', 'created_at', 'created_by']
        widgets = {
            'original_sale': forms.Select(attrs={'class': 'form-select'}),
            'return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'stock_return_done': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'amount_refund_done': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CounterSaleReturnItemForm(forms.ModelForm):
    class Meta:
        model = CounterSaleReturnItem
        exclude = ['amount']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control qty-input', 'step': '0.001'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control rate-input', 'step': '0.01'}),
        }


CounterSaleReturnItemFormSet = inlineformset_factory(
    CounterSaleReturn, CounterSaleReturnItem,
    form=CounterSaleReturnItemForm,
    extra=1,
    can_delete=True,
)


# ── Spares Issue Alteration Forms ─────────────────────────

class SparesIssueAlterationForm(forms.ModelForm):
    class Meta:
        model = SparesIssueAlteration
        exclude = ['spares_total', 'labour_total', 'outwork_total', 'total', 'updated_total', 'created_at', 'created_by']
        widgets = {
            'job_card': forms.TextInput(attrs={'class': 'form-control'}),
            'godown': forms.Select(attrs={'class': 'form-select'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'individual_discount': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SparesIssueAlterationItemForm(forms.ModelForm):
    class Meta:
        model = SparesIssueAlterationItem
        exclude = ['total']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control qty-input', 'step': '0.001'}),
            'rack': forms.Select(attrs={'class': 'form-select rack-select'}),
            'bin': forms.Select(attrs={'class': 'form-select bin-select'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control rate-input', 'step': '0.01'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class SparesIssueAlterationDeletedForm(forms.ModelForm):
    class Meta:
        model = SparesIssueAlterationDeleted
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control qty-input', 'step': '0.001'}),
            'tool_status': forms.Select(attrs={'class': 'form-select'}),
            'rack': forms.Select(attrs={'class': 'form-select rack-select'}),
            'bin': forms.Select(attrs={'class': 'form-select bin-select'}),
            'ref_no': forms.TextInput(attrs={'class': 'form-control'}),
        }


SparesIssueItemFormSet = inlineformset_factory(
    SparesIssueAlteration, SparesIssueAlterationItem,
    form=SparesIssueAlterationItemForm,
    extra=1,
    can_delete=True,
)

SparesIssueDeletedFormSet = inlineformset_factory(
    SparesIssueAlteration, SparesIssueAlterationDeleted,
    form=SparesIssueAlterationDeletedForm,
    extra=1,
    can_delete=True,
)