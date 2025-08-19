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

def generate_payu_hash(params, salt):
    """
    Generate SHA-512 hash for PayU transactions.
    Follows: sha512(key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5||||||SALT)
    """
    data = [
        params.get('key', ''),
        params.get('txnid', ''),
        params.get('amount', ''),
        params.get('productinfo', ''),
        params.get('firstname', ''),
        params.get('email', ''),
        params.get('udf1', ''),
        params.get('udf2', ''),
        params.get('udf3', ''),
        params.get('udf4', ''),
        params.get('udf5', ''),
        '', '', '', '', ''  # udf6~udf10 (empty unless used)
    ]
    hash_string = "|".join(str(x) for x in data) + "|" + salt
    hash_value = sha512(hash_string.encode('utf-8')).hexdigest().lower()
    logger.debug(f"PayU hash string: {hash_string}")
    logger.debug(f"PayU generated hash: {hash_value}")
    return hash_value

def verify_payment(txnid):
    """
    Verify transaction status with PayU.
    """
    try:
        url = "https://info.payu.in/merchant/postservice?form=2"
        params = {
            "key": settings.PAYU_MERCHANT_KEY,
            "txnid": txnid,
            "amount": "",
            "productinfo": "",
            "firstname": "",
            "email": "",
            "udf1": "",
            "udf2": "",
            "udf3": "",
            "udf4": "",
            "udf5": "",
        }
        hash_string = "{key}|verify_payment|{txnid}|||||||||{salt}".format(
            key=settings.PAYU_MERCHANT_KEY, txnid=txnid, salt=settings.PAYU_MERCHANT_SALT)
        hash_value = sha512(hash_string.encode('utf-8')).hexdigest().lower()
        payload = {
            "key": settings.PAYU_MERCHANT_KEY,
            "command": "verify_payment",
            "var1": txnid,
            "hash": hash_value
        }
        response = requests.post(url, data=payload)
        response_data = response.json()
        logger.debug(f"Verification response for txnid {txnid}: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"Error verifying payment for txnid {txnid}: {str(e)}")
        return None
