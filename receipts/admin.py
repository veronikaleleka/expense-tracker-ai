from django.contrib import admin
from .models import Receipt, Item

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'date', 'total_amount')
    inlines = [ItemInline]
