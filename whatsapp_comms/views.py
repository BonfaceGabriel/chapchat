# retail_saas/whatsapp_comms/views.py

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import requests
import json

# Import the models we created in the last step
from .models import Customer, Conversation
from sellers.models import SellerProfile
from products.models import Product # Import the Product model

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    # GET request logic for webhook verification (no changes needed here)
    if request.method == 'GET':
        verify_token = settings.WHATSAPP_VERIFY_TOKEN
        if request.query_params.get('hub.mode') == 'subscribe' and request.query_params.get('hub.verify_token') == verify_token:
            return HttpResponse(request.query_params.get('hub.challenge'), status=200)
        return HttpResponse('Verification failed', status=403)

    # POST request logic for incoming events
    if request.method == 'POST':
        data = request.data
        print(f"--- Incoming Meta Webhook ---\n{json.dumps(data, indent=2)}\n-----------------------------")

        try:
            # We need to parse the nested structure of Meta's payload safely
            value = data['entry'][0]['changes'][0]['value']
            
            # Check if the webhook is a user message
            if 'messages' in value:
                message_details = value['messages'][0]
                if message_details['type'] == 'text':
                    business_phone_number_id = value['metadata']['phone_number_id']
                    customer_phone = message_details['from']
                    incoming_msg_text = message_details['text']['body'].lower().strip()
                    
                    # --- CORE STATEFUL LOGIC ---
                    # This entire block is new or significantly changed
                    try:
                        # 1. Identify the Seller
                        seller_profile = SellerProfile.objects.get(whatsapp_phone_number_id=business_phone_number_id)
                        print(f"Identified Seller: {seller_profile.user.username}")

                        # 2. Identify or Create the Customer
                        customer, created_cust = Customer.objects.get_or_create(phone_number=customer_phone)
                        if created_cust:
                            print(f"New customer created: {customer.phone_number}")

                        # 3. Get or Create the Conversation
                        conversation, created_conv = Conversation.objects.get_or_create(
                            customer=customer,
                            seller=seller_profile
                        )
                        if created_conv:
                            print(f"New conversation started for customer {customer.phone_number}")
                        
                        print(f"Current conversation state: {conversation.state}")

                        # 4. Process the message using the conversation context
                        response_text = process_message(conversation, incoming_msg_text)

                        # 5. Send the reply if one was generated
                        if response_text:
                            send_whatsapp_message(customer.phone_number, response_text)

                    except SellerProfile.DoesNotExist:
                        print(f"ERROR: No seller found for WhatsApp Phone Number ID: {business_phone_number_id}")
                    except Exception as e:
                        print(f"An unexpected error occurred during processing: {e}")
                        send_whatsapp_message(customer_phone, "Sorry, a system error occurred. Please try again later.")

            elif 'statuses' in value:
                status_details = value['statuses'][0]
                print(f"Received status update: '{status_details['status']}' for message {status_details['id']}")
            else:
                print("Received an unhandled webhook type (not a message or status).")

        except (KeyError, IndexError) as e:
            print(f"Could not parse incoming webhook. Structure was not as expected. Error: {e}")

        return JsonResponse({"status": "ok"}, status=200)


def process_message(conversation, message_text):
    """
    The "brain" of the chatbot. Determines the reply based on conversation state.
    This function is now more powerful because it receives the full 'conversation' object.
    """
    state = conversation.state
    seller = conversation.seller
    # Default response if no other logic matches
    response_text = "Sorry, I'm not quite sure what you mean. You can always ask to 'see products'."

    # --- State Machine Logic ---
    if state == Conversation.ConversationState.STARTED:
        response_text = f"Hello! Welcome to {seller.company_name or seller.user.username}. How can I help? You can ask me to 'show products'."
        # Transition to the next state
        conversation.state = Conversation.ConversationState.AWAITING_PRODUCT_QUERY
    
    elif state == Conversation.ConversationState.AWAITING_PRODUCT_QUERY:
        # Look for keywords to trigger a product search
        if 'product' in message_text or 'show' in message_text or 'see' in message_text:
            # Fetch products for THIS SPECIFIC seller from the database
            products = seller.products.filter(is_active=True)[:5] # Get first 5 active products
            
            if products.exists():
                # Format the product list for a clean WhatsApp message
                product_list_text = "\n".join([f"- {p.name} (${p.price})" for p in products])
                response_text = f"Here are some of our products:\n{product_list_text}\n\nTell me the name of a product to learn more or type 'menu'."
            else:
                response_text = "Sorry, we don't have any products available at the moment."
        else:
            response_text = "I can help you with products. Try saying 'show me your products' or type 'menu'."
    
    # Save the updated state to the database for the next interaction
    conversation.save()
    return response_text


def send_whatsapp_message(recipient_phone, message_text):
    """
    Helper function to send a message using the Meta Cloud API. (No changes needed here)
    """
    # ... (This function remains the same as before) ...
    api_url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": recipient_phone, "type": "text", "text": {"body": message_text}}

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Successfully sent message to {recipient_phone}.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Meta Cloud API message: {e.response.text}")