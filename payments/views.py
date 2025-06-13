from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from orders.models import Order
import json

# We can reuse the whatsapp_comms send_whatsapp_message helper
from whatsapp_comms.views import send_whatsapp_message

@api_view(['POST'])
@permission_classes([AllowAny]) # This must be a public endpoint for M-Pesa to reach
def mpesa_callback(request):
    """
    Listens for the callback from M-Pesa after an STK Push transaction.
    """
    # We don't need CSRF exemption because DRF's @api_view handles it for POST
    
    callback_data = request.data
    print(f"--- M-Pesa Callback Received ---\n{json.dumps(callback_data, indent=2)}\n--------------------------")

    # Safely extract data from the nested JSON structure
    try:
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        merchant_request_id = stk_callback.get('MerchantRequestID')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        # Find the corresponding order in our database using the CheckoutRequestID
        order = Order.objects.get(mpesa_checkout_request_id=checkout_request_id)
        customer_phone = order.customer.phone_number

        # Check if the payment was successful
        if result_code == 0:
            print(f"Payment successful for Order #{order.id}.")
            # Payment was successful
            order.status = Order.OrderStatus.PENDING_APPROVAL # Or PROCESSING, based on your workflow
            order.payment_status = 'PAID' # You might want a separate payment_status field
            
            # Extract and save M-Pesa transaction details
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            for item in callback_metadata:
                if item['Name'] == 'MpesaReceiptNumber':
                    order.payment_transaction_id = item['Value']
            
            order.save()

            # Notify the customer
            confirmation_message = (
                f"✅ Payment successful!\n\n"
                f"Thank you for your order. Your Order ID is *#{order.id}*.\n\n"
                f"We have received your payment of KES {order.total_amount:.2f}. "
                "We will begin processing it shortly and notify you of updates."
            )
            send_whatsapp_message(customer_phone, confirmation_message)
            
            # TODO: Notify the seller of the new order via WhatsApp

        else:
            # Payment failed or was cancelled by the user
            print(f"Payment failed for Order #{order.id}. Reason: {result_desc}")
            order.status = Order.OrderStatus.FAILED # Or back to IN_PROGRESS to allow retry
            order.save()

            # Notify the customer of the failure
            failure_message = (
                f"❌ Payment Failed\n\n"
                f"The payment for your order #{order.id} was not completed. "
                f"Reason: {result_desc}\n\n"
                "You can restart the checkout process by typing 'cart'."
            )
            send_whatsapp_message(customer_phone, failure_message)

    except Order.DoesNotExist:
        print(f"ERROR: Received M-Pesa callback for an unknown CheckoutRequestID: {checkout_request_id}")
        # We don't reply because we don't know who the customer is
    except (KeyError, IndexError) as e:
        print(f"ERROR: Malformed M-Pesa callback data. Error: {e}")
    
    # Always return a success response to M-Pesa to acknowledge receipt
    return Response({"ResultCode": 0, "ResultDesc": "Accepted"}, status=200)