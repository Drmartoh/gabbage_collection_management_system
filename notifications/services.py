"""
SMS sending service - API-ready.
Configure GCMS_SMS_API_URL, GCMS_SMS_API_KEY, GCMS_SMS_SENDER_ID in settings.
"""
import logging
from django.conf import settings
from .models import SMSLog

logger = logging.getLogger(__name__)


def send_sms(recipient: str, message: str) -> SMSLog:
    """
    Send SMS via configured API. Returns SMSLog.
    Override or set GCMS_SMS_API_* in .env for your provider (e.g. Africa's Talking, Twilio).
    """
    log = SMSLog.objects.create(recipient=recipient, message=message, status='pending')
    api_url = getattr(settings, 'GCMS_SMS_API_URL', None)
    api_key = getattr(settings, 'GCMS_SMS_API_KEY', None)
    if not api_url or not api_key:
        logger.warning("SMS API not configured. Set GCMS_SMS_API_URL and GCMS_SMS_API_KEY.")
        log.status = 'failed'
        log.error_message = "SMS API not configured"
        log.save()
        return log
    try:
        import requests
        from datetime import datetime
        sender = getattr(settings, 'GCMS_SMS_SENDER_ID', 'GCMS')
        # Example payload - adapt to your provider
        payload = {
            'to': recipient,
            'message': message,
            'sender_id': sender,
        }
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        if resp.ok:
            log.status = 'sent'
            log.sent_at = datetime.now()
            log.external_id = resp.json().get('id', '') or str(resp.text)[:100]
            log.save()
        else:
            log.status = 'failed'
            log.error_message = resp.text[:500]
            log.save()
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)[:500]
        log.save()
        logger.exception("SMS send failed")
    return log
