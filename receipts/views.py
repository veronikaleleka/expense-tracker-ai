import hashlib
from decimal import Decimal

from django.db import transaction
from django.shortcuts import render
from datetime import date
from django.utils.dateparse import parse_date

from . import ai
from .forms import ReceiptUploadForm
from .models import Item, Receipt


def to_decimal(value):
    return Decimal(str(value).replace(',', '.'))

def parse_receipt_date(value):
    try:
        return parse_date(str(value or ''))
    except ValueError:
        return None


def upload_receipt(request):
    receipt = None
    error = None
    warnings = []
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

                    receipt_date = parse_receipt_date(data.get('date'))
                    if receipt_date is None:
                        receipt_date = date.today()
                        warnings.append('Date not found on the receipt, upload date used.')

                    items_data = data.get('items') or []
                    items_sum = sum(
                        (to_decimal(i['price']) * int(i.get('quantity') or 1)
                         for i in items_data),
                        Decimal('0'),
                    )

                    if data.get('total_amount') is None:
                        total = items_sum
                        warnings.append('Total not found on the receipt, item sum used.')
                    else:
                        total = to_decimal(data['total_amount'])
                        if abs(items_sum - total) > Decimal('0.05'):
                            warnings.append(
                                f'Items sum ({items_sum}) differs from total ({total}).'
                            )

                    with transaction.atomic():
                        receipt = Receipt.objects.create(
                            store_name=data.get('store_name') or 'Unknown store',
                            date=receipt_date,
                            total_amount=total,
                            file_hash=file_hash,
                        )
                        for entry in items_data:
                            category = entry.get('category')
                            if category not in Item.Category.values:
                                category = Item.Category.OTHER
                            Item.objects.create(
                                receipt=receipt,
                                name=entry['name'],
                                price=to_decimal(entry['price']),
                                quantity=int(entry.get('quantity') or 1),
                                category=category,
                            )
                except Exception as e:
                    receipt = None
                    warnings = []
                    error = f'Could not process receipt: {e}'
    else:
        form = ReceiptUploadForm()

    return render(request, 'receipts/upload.html', {
        'form': form,
        'receipt': receipt,
        'error': error,
        'warning': ' '.join(warnings) or None,
        'duplicate': duplicate,
    })