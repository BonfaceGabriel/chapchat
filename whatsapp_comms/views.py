# retail_saas/whatsapp_comms/views.py

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import requests
import json

# Import the models 
from .models import Customer, Conversation
from sellers.models import SellerProfile
from products.models import Product # Import the Product model
from .handlers import ( 
    handle_state_started,
    handle_state_awaiting_command,
    handle_state_awaiting_product_selection,
    handle_state_awaiting_product_action,
    handle_state_awaiting_size_selection,
    handle_state_awaiting_quantity,
    handle_state_viewing_cart,
    handle_state_awaiting_delivery_choice,    
    handle_state_awaiting_delivery_address,
    handle_state_awaiting_payment_confirmation,
)


# The mapping of a state to its handler function
STATE_HANDLERS = {
    Conversation.ConversationState.STARTED: handle_state_started,
    Conversation.ConversationState.AWAITING_COMMAND: handle_state_awaiting_command,
    Conversation.ConversationState.AWAITING_PRODUCT_SELECTION: handle_state_awaiting_product_selection,
    Conversation.ConversationState.AWAITING_PRODUCT_ACTION: handle_state_awaiting_product_action,
    Conversation.ConversationState.AWAITING_SIZE_SELECTION: handle_state_awaiting_size_selection, 
    Conversation.ConversationState.AWAITING_QUANTITY: handle_state_awaiting_quantity,
    Conversation.ConversationState.VIEWING_CART: handle_state_viewing_cart,
    Conversation.ConversationState.AWAITING_DELIVERY_CHOICE: handle_state_awaiting_delivery_choice, 
    Conversation.ConversationState.AWAITING_DELIVERY_ADDRESS: handle_state_awaiting_delivery_address,
    Conversation.ConversationState.AWAITING_PAYMENT_CONFIRMATION: handle_state_awaiting_payment_confirmation,
    # We'll add more handlers here as we create them
}

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
            value = data['entry'][0]['changes'][0]['value']
            
            if 'messages' in value:
                message_details = value['messages'][0]
                business_phone_number_id = value['metadata']['phone_number_id']
                customer_phone = message_details['from']

                # --- (+) REVISED LOGIC TO HANDLE BOTH MESSAGE TYPES ---
                # Check if it's a text message OR an interactive (button) message
                if message_details.get('type') in ['text', 'interactive']:
                    # --- CORE LOGIC WITH DATABASE INTERACTION ---
                    try:
                        seller_profile = SellerProfile.objects.get(whatsapp_phone_number_id=business_phone_number_id)
                        customer, _ = Customer.objects.get_or_create(phone_number=customer_phone)
                        conversation, _ = Conversation.objects.get_or_create(customer=customer, seller=seller_profile)
                        
                        print(f"Identified Seller: {seller_profile.user.username}")
                        print(f"Current conversation state: {conversation.state}")

                        # Pass the full message_details dictionary to the processor
                        response_payload = process_message(conversation, message_details)

                        if response_payload:
                            send_whatsapp_message(customer.phone_number, response_payload)

                    except SellerProfile.DoesNotExist:
                        print(f"ERROR: No seller found for WhatsApp Phone Number ID: {business_phone_number_id}")
                    except Exception as e:
                        print(f"An unexpected error occurred during processing: {e}")
                        send_whatsapp_message(customer_phone, "Sorry, a system error occurred. Please try again later.")
                else:
                    print(f"Received a message of unhandled type: {message_details.get('type')}")

            elif 'statuses' in value:
                status_details = value['statuses'][0]
                print(f"Received status update: '{status_details['status']}' for message {status_details['id']}")
            else:
                print("Received an unhandled webhook type.")

        except (KeyError, IndexError) as e:
            print(f"Could not parse incoming webhook. Structure was not as expected. Error: {e}")

        return JsonResponse({"status": "ok"}, status=200)

def process_message(conversation, message_details):
    """
    Main router. Decides which handler to call based on global commands,
    interactive replies, or the current conversation state.
    """
    message_text = message_details.get('text', {}).get('body', '').lower().strip()
    interactive_data = message_details.get('interactive', {})
    reply_type = interactive_data.get('type')
    
    reply_id = None
    if reply_type == 'button_reply':
        reply_id = interactive_data.get('button_reply', {}).get('id')
    elif reply_type == 'list_reply':
        reply_id = interactive_data.get('list_reply', {}).get('id')

    # --- Router Logic ---
    handler = None
    
    # 1. Check for global commands that override any state
    if message_text in ['hi', 'hello', 'hey', 'menu'] or reply_id in ['show_menu', 'keep_shopping']:
        handler = handle_state_awaiting_command # This handler's job is to show the main menu
    elif message_text == 'view cart' or reply_id == 'view_cart':
        handler = handle_state_viewing_cart

    # 2. If no global command, use the handler for the current state
    else:
        handler = STATE_HANDLERS.get(conversation.state)

    # 3. Call the handler to get the response
    if handler:
        response_payload = handler(conversation, message_details)
    else:
        # Fallback if state is not in our handler map
        response_payload = "Sorry, I've gotten a bit confused. Let's start over by typing 'menu'."
        conversation.state = Conversation.ConversationState.AWAITING_COMMAND
    
    conversation.save()
    print(f"SAVED conversation. New state is: {conversation.state}")
    
    return response_payload

def send_whatsapp_message(recipient_phone, message_payload):
    """
    Sends a message using the Meta Cloud API.
    The payload can be a simple text string or a complex dictionary for interactive messages.
    This version automatically adds a helpful footer to interactive messages.
    """
    api_url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # The base payload structure
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
    }

    # Check if message_payload is a string (for simple text) or a dict (for interactive messages)
    if isinstance(message_payload, str):
        data['type'] = 'text'
        data['text'] = {'body': message_payload}
    elif isinstance(message_payload, dict):
        # For complex messages like buttons, merge the payload
        data.update(message_payload)
        
        # Automatically add a footer to all interactive messages for better UX
        if data.get('type') == 'interactive':
            # Ensure the path exists before trying to assign to it
            if 'action' not in data['interactive']:
                data['interactive']['action'] = {}
            # Add the footer text
            data['interactive']['footer'] = {
                "text": "Reply 'menu' for options or 'view cart' to view your cart."
            }
    else:
        print(f"Error: Invalid message_payload type provided: {type(message_payload)}")
        return

    print(f"--- Sending API Request to Meta ---\n{json.dumps(data, indent=2)}\n---------------------------------")

    try:
        response = requests.post(api_url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Successfully sent message to {recipient_phone}.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Meta Cloud API message: {e.response.text if e.response else e}")