# retail_saas/whatsapp_comms/views.py
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import requests
import json
from .models import Customer, Conversation
from sellers.models import SellerProfile

@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    # GET request is for one-time webhook verification
    if request.method == 'GET':
        if request.query_params.get('hub.mode') == 'subscribe' and request.query_params.get('hub.verify_token') == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(request.query_params.get('hub.challenge'), status=200)
        return HttpResponse('Verification failed', status=403)

    # POST request is for incoming messages
    if request.method == 'POST':
        data = request.data
        print(f"--- Incoming Meta Webhook ---\n{json.dumps(data, indent=2)}\n-----------------------------")

        try:
            # Extract key information from Meta's complex JSON payload
            business_phone_number_id = data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
            message_details = data['entry'][0]['changes'][0]['value']['messages'][0]
            customer_phone = message_details['from']
            incoming_msg_text = message_details['text']['body'].lower().strip()

            # --- Core Logic Starts Here ---
            seller_profile = SellerProfile.objects.get(whatsapp_phone_number_id=business_phone_number_id)
            customer, _ = Customer.objects.get_or_create(phone_number=customer_phone)
            conversation, _ = Conversation.objects.get_or_create(customer=customer, seller=seller_profile)
            
            # Process the message and get a reply
            response_text = process_message(conversation, incoming_msg_text)
            
            # Send the reply back to the user
            if response_text:
                send_whatsapp_message(customer.phone_number, response_text)

        except (KeyError, IndexError, SellerProfile.DoesNotExist) as e:
            print(f"Could not process webhook: {e}. Payload might not be a user text message or seller not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        return JsonResponse({"status": "ok"}, status=200)

def process_message(conversation, message_text):
    # This is our "state machine" brain
    state = conversation.state
    seller = conversation.seller
    response_text = "Sorry, I'm not quite sure what you mean. Try asking to 'see products'."

    if state == Conversation.ConversationState.STARTED:
        response_text = f"Hello! Welcome to {seller.company_name or seller.user.username}. How can I help? You can ask to 'show products'."
        conversation.state = Conversation.ConversationState.AWAITING_PRODUCT_QUERY
    
    elif state == Conversation.ConversationState.AWAITING_PRODUCT_QUERY:
        if 'product' in message_text or 'show' in message_text:
            products = seller.products.filter(is_active=True)[:5]
            if products:
                product_list = "\n".join([f"- {p.name} (${p.price})" for p in products])
                response_text = f"Here are some of our products:\n{product_list}\n\nTell me the name of a product to learn more."
            else:
                response_text = "Sorry, we don't have any products available at the moment."
        else:
            response_text = "I can help you with products. Try saying 'show me your products'."
    
    conversation.save()
    return response_text

def send_whatsapp_message(recipient_phone, message_text):
    # This function sends the reply using the Meta API
    api_url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": recipient_phone, "type": "text", "text": {"body": message_text}}

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Successfully sent message to {recipient_phone}.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Meta Cloud API message: {e.response.text}")