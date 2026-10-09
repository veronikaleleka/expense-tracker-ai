import hashlib

from django.shortcuts import render

from .forms import ReceiptUploadForm
from .models import Receipt


def upload_receipt(request):
    result = None
    if request.method == 'POST':
        form = ReceiptUploadForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.cleaned_data['image'].read()
            file_hash = hashlib.md5(content).hexdigest()[:10]
            result = {
                'hash': file_hash,
                'duplicate': Receipt.objects.filter(file_hash=file_hash).exists(),
            }
    else:
        form = ReceiptUploadForm()
    return render(request, 'receipts/upload.html', {'form': form, 'result': result})
