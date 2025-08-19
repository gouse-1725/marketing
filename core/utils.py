import requests
from django.conf import settings
import logging
from hashlib import sha512

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
    

def generate_payu_hash(params, salt):
    """Generate SHA-512 hash for PayU transactions."""
    try:
        hash_string = f"{params['key']}|{params['txnid']}|{params['amount']}|{params['productinfo']}|{params['firstname']}|{params['email']}|{params.get('udf1', '')}|{params.get('udf2', '')}|{params.get('udf3', '')}|{params.get('udf4', '')}|{params.get('udf5', '')}||||||{salt}"
        hash_value = sha512(hash_string.encode()).hexdigest().lower()
        logger.debug(f"Generated hash for params {params}: {hash_value}")
        return hash_value
    except Exception as e:
        logger.error(f"Error generating PayU hash: {str(e)}")
        raise

def verify_payment(txnid):
    """Verify transaction status with PayU."""
    try:
        url = "https://info.payu.in/merchant/postservice?form=2"
        payload = {
            "key": settings.PAYU_MERCHANT_KEY,
            "command": "verify_payment",
            "var1": txnid,
            "hash": generate_payu_hash({
                "key": settings.PAYU_MERCHANT_KEY,
                "command": "verify_payment",
                "var1": txnid
            }, settings.PAYU_MERCHANT_SALT)
        }
        response = requests.post(url, data=payload)
        response_data = response.json()
        logger.debug(f"Verification response for txnid {txnid}: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"Error verifying payment for txnid {txnid}: {str(e)}")
        return None

def send_sms(recipients, message):
    """Placeholder for SMS sending (replace with your actual SMS provider logic)."""
    # Your existing SMS logic here
    url = "https://api.example.com/send_sms"
    payload = {
        "recipients": recipients,  
        "message": message
    }
    headers = {
        "Authorization": f"Bearer {settings.MSG91_AUTH_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to send SMS: {response.text}")
        return {"type": "error", "message": "Failed to send SMS"}
    response_data = response.json()
    if response_data.get("type") != "success":
        logger.error(f"SMS sending failed: {response_data.get('message')}")
        return {"type": "error", "message": response_data.get("message")}
    logger.info(f"SMS sent successfully: {response_data}")
    recipients = ', '.join(recipients) if isinstance(recipients, list) else recipients
    message = message[:160]
    
    logger.info(f"SMS sent to {recipients}: {message}")
    return {"type": "success"}  # Mock response for testing