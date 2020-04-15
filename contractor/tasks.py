from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import F
from django.utils import timezone

from celery import shared_task
import requests

from .models import Contract


@shared_task(name='fetch_contract_result')
def fetch_contract_result(contract_id):
    try:
        contract = Contract.objects.get(id=contract_id)
    except Contract.DoesNotExist:
        return

    Contract.objects.filter(id=contract_id).update(
        version=F('version') + 1,
        updated=timezone.now()
    )
    contract.version += 1

    for filename, url in contract.get_source_files():
        download_file(contract, filename, url)


def download_file(contract, filename, url):
    path = contract.get_file_path(filename)
    response = requests.get(url)
    # FIXME: returned path is not stored, assumed to be the same
    default_storage.save(path, ContentFile(response.content))
