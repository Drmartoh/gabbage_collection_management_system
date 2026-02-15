"""
SMS sending service - API-ready.
Configure via Settings page (HERE Maps & SMS) or .env: GCMS_SMS_API_URL, GCMS_SMS_API_KEY, GCMS_SMS_SENDER_ID.
"""
import logging
from django.conf import settings
from .models import SMSLog

logger = logging.getLogger(__name__)


def _get_sms_config():
    """Return (api_url, api_key, sender_id). Values from SystemSetting (Settings page) first, then .env."""
    try:
        from core.models import SystemSetting
        url = (SystemSetting.get_value('sms_api_url', '') or '').strip()
        key = (SystemSetting.get_value('sms_api_key', '') or '').strip()
        sender = (SystemSetting.get_value('sms_sender_id', '') or '').strip() or 'GCMS'
        if url and key:
            return url, key, sender
    except Exception:
        pass
    return (
        getattr(settings, 'GCMS_SMS_API_URL', '') or '',
        getattr(settings, 'GCMS_SMS_API_KEY', '') or '',
        getattr(settings, 'GCMS_SMS_SENDER_ID', 'GCMS') or 'GCMS',
    )


def is_sms_configured():
    """True if SMS API URL and key are set (Settings page or .env)."""
    url, key, _ = _get_sms_config()
    return bool(url and key)


def send_sms(recipient: str, message: str) -> SMSLog:
    """
    Send SMS via configured API. Returns SMSLog.
    Set URL and key in Settings → SMS or in .env for your provider (e.g. Africa's Talking, Twilio).
    """
    log = SMSLog.objects.create(recipient=recipient, message=message, status='pending')
    api_url, api_key, sender = _get_sms_config()
    if not api_url or not api_key:
        logger.warning("SMS API not configured. Set in Settings → SMS or GCMS_SMS_API_URL / GCMS_SMS_API_KEY in .env.")
        log.status = 'failed'
        log.error_message = "SMS API not configured"
        log.save()
        return log
    try:
        import requests
        from datetime import datetime
        # Example payload - adapt to your provider
        payload = {
            'to': recipient,
            'message': message,
            'sender_id': sender or 'GCMS',
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
