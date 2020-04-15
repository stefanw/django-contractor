from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Contract
from .tasks import fetch_contract_result


@csrf_exempt
@require_POST
def webhook(request, token):
    try:
        contract = Contract.objects.get(token=token)
    except Contract.DoesNotExist:
        return JsonResponse({})

    contract.webhook_log = request.body.decode('utf-8')
    contract.save()

    fetch_contract_result.delay(contract.id)

    return JsonResponse({})
