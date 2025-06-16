from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from orders.models import Order
from django.db import transaction
import json

# We can reuse the whatsapp_comms send_whatsapp_message helper
from whatsapp_comms.views import send_whatsapp_message

@api_view(['POST'])
@permission_classes([AllowAny])
def mpesa_callback(request):
    """
    Listens for the callback from M-Pesa after an STK Push transaction.
    Updates order status, decrements inventory, and notifies all parties.
    """
    callback_data = request.data
    print(f"--- M-Pesa Callback Received ---\n{json.dumps(callback_data, indent=2)}\n--------------------------")

    try:
        stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        
        if not checkout_request_id:
            print("Callback received without CheckoutRequestID.")
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"}, status=200)

        # Use a database transaction for safety
        with transaction.atomic():
            # Find the corresponding order and lock it for updating
            order = Order.objects.select_for_update().get(mpesa_checkout_request_id=checkout_request_id)

            # --- Check 1: Has this transaction already been processed? ---
            if order.status != Order.OrderStatus.PENDING_PAYMENT:
                print(f"Received a duplicate or late callback for already processed Order #{order.id}.")
                return Response({"ResultCode": 0, "ResultDesc": "Accepted"}, status=200)

            # --- Check 2: Was the payment successful? ---
            if result_code == 0:
                print(f"Payment successful for Order #{order.id}. Updating status and inventory.")
                
                # Update Order Status
                order.status = Order.OrderStatus.PENDING_APPROVAL
                
                # Save M-Pesa Transaction ID
                callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in callback_metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        order.payment_transaction_id = item.get('Value')
                
                # Decrement Inventory for each item in the order
                for item in order.items.all():
                    product = item.product
                    if product:
                        if product.inventory_count >= item.quantity:
                            product.inventory_count -= item.quantity
                            product.save()
                        else:
                            print(f"WARNING: Insufficient stock for Product ID {product.id} on Order {order.id}.")
                            # In a full system, you might flag this order for manual review
                
                order.save()

                # --- Notify Customer ---
                customer_phone = order.customer.phone_number
                customer_message = (
                    f"✅ Payment successful!\n\n"
                    f"Thank you for your order. Your Order ID is *#{order.id}*.\n\n"
                    f"We have received your payment of KES {order.total_amount:.2f}. "
                    "We will begin processing it shortly."
                )
                send_whatsapp_message(customer_phone, customer_message)
                
                # --- Notify Seller ---
                seller = order.seller
                if seller.notification_phone_number:
                    order_items_summary = "\n".join(
                        [f"- {item.quantity} x {item.product.name}" for item in order.items.all()]
                    )
                    seller_message = (
                        f"🎉 New Paid Order!\n\n"
                        f"You have a new order (#{order.id}) for *KES {order.total_amount:.2f}*.\n\n"
                        f"Items:\n{order_items_summary}\n\n"
                        "Please log in to your dashboard to approve and fulfill the order."
                    )
                    send_whatsapp_message(seller.notification_phone_number, seller_message)
                else:
                    print(f"Seller {seller.user.username} has no notification number set. Skipping notification.")

            else:
                # Payment failed or was cancelled
                result_desc = stk_callback.get('ResultDesc', 'Payment was not completed.')
                print(f"Payment failed for Order #{order.id}. Reason: {result_desc}")
                order.status = Order.OrderStatus.FAILED
                order.save()

                # Notify customer of failure
                customer_phone = order.customer.phone_number
                failure_message = (
                    f"❌ Payment Failed\n\n"
                    f"The payment for your order #{order.id} was not completed.\n"
                    f"Reason: {result_desc}\n\n"
                    "You can restart the checkout process by typing 'cart'."
                )
                send_whatsapp_message(customer_phone, failure_message)

    except Order.DoesNotExist:
        print(f"ERROR: Received M-Pesa callback for an unknown CheckoutRequestID: {checkout_request_id}")
    except Exception as e:
        print(f"An unexpected error occurred in mpesa_callback: {e}")

    return Response({"ResultCode": 0, "ResultDesc": "Accepted"}, status=200)