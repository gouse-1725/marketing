import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_sms(mobile_numbers, message):
    """
    Send SMS using MSG91 API.
    :param mobile_numbers: List of mobile numbers (with country code, e.g., ['+919999999999'])
    :param message: The message to send
    :return: Response from MSG91 API
    """
    url = "https://api.msg91.com/api/v2/sendsms"
    payload = {
        "sender": settings.MSG91_SENDER_ID,
        "route": "4",  # Transactional SMS route
        "country": "91",  # Country code for India
        "sms": [
            {
                "message": message,
                "to": mobile_numbers
            }
        ]
    }
    headers = {
        "authkey": settings.MSG91_AUTH_KEY,
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"SMS sent successfully: {response.json()}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error sending SMS: {e}")
        return None