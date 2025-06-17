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
def initiate_stk_push(phone_number, amount, order_id):
    """
    Initiates an M-Pesa STK Push request.
    This version dynamically builds the callback URL from environment variables.
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
    
    password_str = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(password_str.encode('utf-8')).decode('utf-8')

    # Format phone number
    if phone_number.startswith('+'):
        formatted_phone = phone_number[1:]
    elif phone_number.startswith('0'):
        formatted_phone = f"254{phone_number[1:]}"
    else:
        formatted_phone = phone_number

    # --- THIS IS THE CRUCIAL FIX ---
    # Build the callback URL dynamically from the APP_DOMAIN env var
    # instead of hardcoding it.
    app_domain = settings.APP_DOMAIN
    print(f"APP_DOMAIN: {settings.APP_DOMAIN}") # We get this from our settings file
    if not app_domain:
        print("ERROR: APP_DOMAIN environment variable is not set. Cannot form callback URL.")
        return None
    
    # Ensure the domain starts with https:// for production
    if not app_domain.startswith('http'):
         app_domain = f"https://{app_domain}"

    callback_url = f"{app_domain}/api/payments/mpesa-callback/"
    print(f"Using M-Pesa callback URL: {callback_url}")
    
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": formatted_phone,
        "PartyB": shortcode,
        "PhoneNumber": formatted_phone,
        "CallBackURL": callback_url, # Use the dynamically generated URL
        "AccountReference": str(order_id),
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