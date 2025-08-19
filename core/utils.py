# utils.py

import requests
from django.conf import settings
import logging
from hashlib import sha512

logger = logging.getLogger(__name__)

# This is the corrected function
def generate_payu_hash(params, salt):
    """Generate SHA-512 hash for PayU transactions."""
    try:
        # Corrected hash_string with 10 empty UDFs after udf5
        hash_string = (
            f"{params['key']}|{params['txnid']}|{params['amount']}|"
            f"{params['productinfo']}|{params['firstname']}|{params['email']}|"
            f"{params.get('udf1', '')}|{params.get('udf2', '')}|{params.get('udf3', '')}|"
            f"{params.get('udf4', '')}|{params.get('udf5', '')}||||||||||{salt}"
        )
        hash_value = sha512(hash_string.encode()).hexdigest().lower()
        logger.debug(f"Generated hash from string '{hash_string}': {hash_value}")
        return hash_value
    except Exception as e:
        logger.error(f"Error generating PayU hash: {str(e)}")
        raise

def verify_payment(txnid):
    """Verify transaction status with PayU."""
    try:
        # Note: The hash for verify_payment has a different format!
        hash_string = f"{settings.PAYU_MERCHANT_KEY}|verify_payment|{txnid}|{settings.PAYU_MERCHANT_SALT}"
        verification_hash = sha512(hash_string.encode()).hexdigest().lower()
        
        url = "https://info.payu.in/merchant/postservice?form=2"
        payload = {
            "key": settings.PAYU_MERCHANT_KEY,
            "command": "verify_payment",
            "var1": txnid,
            "hash": verification_hash
        }
        
        response = requests.post(url, data=payload)
        response.raise_for_status()
        response_data = response.json()
        logger.debug(f"Verification response for txnid {txnid}: {response_data}")
        return response_data
    except requests.RequestException as e:
        logger.error(f"Error verifying payment for txnid {txnid}: {str(e)}")
        return None

# Your MSG91 SMS function
def send_sms(mobile_numbers, message):
    """
    Send SMS using MSG91 API.
    """
    url = "https://api.msg91.com/api/v2/sendsms"
    payload = {
        "sender": settings.MSG91_SENDER_ID,
        "route": "4",
        "country": "91",
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