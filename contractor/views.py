from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Contract
from .tasks import fetch_contract_result


@csrf_exempt
@require_POST
def webhook(request, token):
    try:
        contract = Contract.objects.get(token=token, webhook_active=True)
    except Contract.DoesNotExist:
        return JsonResponse({})

    contract.webhook_log = request.body.decode('utf-8')
    contract.save()

    fetch_contract_result.delay(contract.id)

    return JsonResponse({})


def redirect_current(request, slug, path):
    contract = get_object_or_404(Contract, slug=slug)
    url = contract.get_absolute_url(filename=path)
    return redirect(url)
