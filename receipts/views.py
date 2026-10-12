import hashlib
from decimal import Decimal

from django.db import transaction
from django.shortcuts import render

from . import ai
from .forms import ReceiptUploadForm
from .models import Item, Receipt


def to_decimal(value):
    return Decimal(str(value).replace(',', '.'))


def upload_receipt(request):
    receipt = None
    error = None
    warning = None
    duplicate = False

    if request.method == 'POST':
        form = ReceiptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data['image'].read()
            file_hash = hashlib.md5(content).hexdigest()[:10]

            if Receipt.objects.filter(file_hash=file_hash).exists():
                duplicate = True
            else:
                try:
                    data = ai.extract_receipt(content)
                    with transaction.atomic():
                        receipt = Receipt.objects.create(
                            store_name=data['store_name'],
                            date=data['date'],
                            total_amount=to_decimal(data['total_amount']),
                            file_hash=file_hash,
                        )
                        for entry in data['items']:
                            category = entry.get('category')
                            if category not in Item.Category.values:
                                category = Item.Category.OTHER
                            Item.objects.create(
                                receipt=receipt,
                                name=entry['name'],
                                price=to_decimal(entry['price']),
                                quantity=int(entry.get('quantity', 1)),
                                category=category,
                            )
                    items_sum = sum(i.price * i.quantity for i in receipt.items.all())
                    if abs(items_sum - receipt.total_amount) > Decimal('0.05'):
                        warning = (
                            f'Items sum ({items_sum}) differs from '
                            f'total ({receipt.total_amount}).'
                        )
                except Exception as e:
                    receipt = None
                    error = f'Could not process receipt: {e}'
    else:
        form = ReceiptUploadForm()

    return render(request, 'receipts/upload.html', {
        'form': form,
        'receipt': receipt,
        'error': error,
        'warning': warning,
        'duplicate': duplicate,
    })