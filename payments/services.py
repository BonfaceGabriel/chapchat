import requests
import base64
from datetime import datetime
from django.conf import settings

# Helper function to get the M-Pesa API access token
def get_mpesa_access_token():
    """
    Fetches the M-Pesa API access token using Basic Auth with consumer key and secret.
    TODO: Cache this token to avoid requesting a new one for every transaction.
    """
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        json_response = response.json()
        return json_response.get('access_token')
    except requests.exceptions.RequestException as e:
        print(f"Error getting M-Pesa access token: {e}")
        return None

# Main function to initiate the STK Push
def initiate_stk_push(phone_number, amount, order_id, callback_url):
    """
    Initiates an M-Pesa STK Push request for a given phone number and amount.
    """
    access_token = get_mpesa_access_token()
    if not access_token:
        print("Failed to get M-Pesa access token. Aborting STK push.")
        return None

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    
    # Generate the password as per M-Pesa guidelines (Base64 of Shortcode+Passkey+Timestamp)
    password_str = f"{shortcode}{passkey}{timestamp}"
    password_bytes = password_str.encode('utf-8')
    password = base64.b64encode(password_bytes).decode('utf-8')

    # Format the phone number to Safaricom's required format (e.g., 254...)
    # Assuming input is like '+2547...' or '07...'. This logic should be robust.
    if phone_number.startswith('+'):
        formatted_phone = phone_number[1:]
    elif phone_number.startswith('0'):
        formatted_phone = f"254{phone_number[1:]}"
    else:
        formatted_phone = phone_number # Assume it's already in the correct format

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline", # Or "CustomerBuyGoodsOnline"
        "Amount": int(amount), # Amount must be an integer
        "PartyA": formatted_phone,
        "PartyB": shortcode,
        "PhoneNumber": formatted_phone,
        "CallBackURL": callback_url,
        "AccountReference": str(order_id), # Must be a string
        "TransactionDesc": f"Payment for Order #{order_id}"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        print("STK Push initiated successfully. Response:", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error initiating STK push: {e.response.text if e.response else e}")
        return None