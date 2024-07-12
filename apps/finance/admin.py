from django.contrib import admin
from .models import Invoice, InvoiceItem, Receipt

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class ReceiptInline(admin.TabularInline):
    model = Receipt
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'term', 'class_for', 'status', 'balance_from_previous_term')
    list_filter = ('session', 'term', 'class_for', 'status')
    search_fields = ('student__surname', 'student__firstname', 'student__registration_number')
    ordering = ('student', 'term')
    inlines = [InvoiceItemInline, ReceiptInline]
    
    def balance(self, obj):
        return obj.balance()
    balance.short_description = 'Balance'

    def amount_payable(self, obj):
        return obj.amount_payable()
    amount_payable.short_description = 'Amount Payable'

    def total_amount_payable(self, obj):
        return obj.total_amount_payable()
    total_amount_payable.short_description = 'Total Amount Payable'

    def total_amount_paid(self, obj):
        return obj.total_amount_paid()
    total_amount_paid.short_description = 'Total Amount Paid'

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'amount')
    list_filter = ('invoice',)
    search_fields = ('invoice__student__surname', 'invoice__student__firstname', 'description')
    ordering = ('invoice',)

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount_paid', 'date_paid', 'comment')
    list_filter = ('invoice',)
    search_fields = ('invoice__student__surname', 'invoice__student__firstname', 'comment')
    ordering = ('invoice', 'date_paid')

