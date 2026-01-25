"""
💳 Toss Payments Webhook Views

토스페이먼츠 Webhook 수신 및 처리.
"""

import json
import hmac
import hashlib

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ...webhook import handle_webhook


@csrf_exempt
@require_POST
def toss_payments_webhook(request: HttpRequest) -> HttpResponse:
    """
    토스페이먼츠 Webhook 수신
    
    Webhook 시그니처 검증 후 처리.
    """
    # Webhook 시그니처 검증
    webhook_secret = getattr(settings, "TOSS_WEBHOOK_SECRET", "")
    signature = request.headers.get("X-Toss-Signature", "")

    if webhook_secret:
        # 시그니처 검증 로직 (토스페이먼츠 문서 참조)
        body = request.body
        expected_signature = hmac.new(
            webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()

        if signature != expected_signature:
            return HttpResponseBadRequest("Invalid signature")

    # 페이로드 파싱
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    # Webhook 처리 (비동기)
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(handle_webhook(payload))

    if result.get("status") == "ok":
        return HttpResponse("OK", status=200)
    else:
        return HttpResponseBadRequest(result.get("error", "Webhook processing failed"))
