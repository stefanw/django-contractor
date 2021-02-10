from django.db.models import F
from django.utils import timezone

from celery import shared_task

from .models import Contract
from .utils import (
    download_and_save_file, resource_to_filename,
    get_integrity_for_resource
)


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
        path = contract.get_file_path(filename)
        download_and_save_file(url, path)

    apply_subresource_integrity.delay(contract.pk)


@shared_task(name='apply_subresource_integrity')
def apply_subresource_integrity(contract_id):
    try:
        contract = Contract.objects.get(id=contract_id)
    except Contract.DoesNotExist:
        return

    lines = []
    for resource in contract.get_resources():
        if resource.url.endswith(('.js', '.css')):
            integrity = get_integrity_for_resource(resource)
            resource.attributes['integrity'] = integrity
        line = resource_to_filename(resource)
        lines.append(line)

    contract.files = '\n'.join(lines)
    contract.save()
