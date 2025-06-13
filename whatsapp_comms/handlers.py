
from .models import Conversation
from products.models import Product
from orders.models import Order, OrderItem
from payments.services import initiate_stk_push

def _send_product_list_message(conversation, products, title="Our Products"):
    """Helper function to build and return an interactive list of products."""
    
    if not products.exists():
        conversation.state = Conversation.ConversationState.AWAITING_COMMAND
        return "Sorry, we don't have any products available right now."
        
    rows = []
    # WhatsApp lists support up to 10 rows per section
    for product in products[:10]:
        rows.append({
            "id": f"select_product_{product.id}",
            "title": str(product.name)[:24],
            "description": f"${product.price}"[:72]
        })
    
    list_payload = {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": title},
            "body": {"text": "Please select an item from the list to see more details."},
            "action": {
                "button": "View Products",
                "sections": [{"title": "Products", "rows": rows}]
            }
        }
    }
    
    # Set the state so the next reply is handled by the product selection logic
    conversation.state = Conversation.ConversationState.AWAITING_PRODUCT_SELECTION
    return list_payload


# Helper function to build and return the interactive message for a single product.
def _send_product_details_interactive(conversation, product):
    """
    Builds and returns the interactive message payload for a single product's details.
    This function also correctly sets the next conversation state.
    """
    body_text = (
        f"*{product.name}*\n\n"
        f"{product.description or 'No description available.'}\n\n"
        f"Price: ${product.price}"
    )
    
    interactive_payload = {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": f"add_to_cart_{product.id}", "title": "Add to Cart 🛒"}},
                    {"type": "reply", "reply": {"id": "show_menu", "title": "Main Menu"}},
                ]
            }
        }
    }
    
    # Store context and transition state for the next step
    conversation.context['viewed_product_id'] = product.id
    conversation.state = Conversation.ConversationState.AWAITING_PRODUCT_ACTION
    return interactive_payload


def handle_state_started(conversation, message_details):
    seller = conversation.seller
    response_text = f"Hello! Welcome to {seller.company_name or seller.user.username}. How can I help you? You can ask me to 'show products' or type 'menu'."
    conversation.state = Conversation.ConversationState.AWAITING_COMMAND
    return response_text

def handle_state_awaiting_command(conversation, message_details):
    """
    This is the main menu handler. It can be triggered by text ('menu') or
    buttons ('show_menu', 'keep_shopping'). Its primary job is to PRESENT the main menu.
    It also handles button clicks FROM that main menu.
    """
    seller = conversation.seller
    button_id = message_details.get('interactive', {}).get('button_reply', {}).get('id')

    # --- Part 1: Process a button click from the main menu itself ---
    if button_id == 'search_by_keyword':
        conversation.state = Conversation.ConversationState.AWAITING_PRODUCT_SELECTION
        return "Great! What kind of product are you looking for? (e.g., 'jacket', 'denim')"
    
    elif button_id == 'view_all_products':
        all_products = seller.products.filter(is_active=True)
        return _send_product_list_message(conversation, all_products, title="Our Full Catalog")

    # The 'view_cart' button is handled by the global router in process_message

    # --- Part 2: If no button was clicked, or it was a text command, SHOW the main menu ---
    body_text = (
        f"You are at the main menu for *{seller.company_name or seller.user.username}*.\n\n"
        "How can I help you?"
    )
    
    menu_payload = {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "search_by_keyword", "title": "🔍 Search for an item"}},
                    {"type": "reply", "reply": {"id": "view_all_products", "title": "Browse All Products"}},
                    {"type": "reply", "reply": {"id": "view_cart", "title": "View Cart 🛒"}}
                ]
            }
        }
    }
    # Set the state so the next reply is handled correctly by this same function
    conversation.state = Conversation.ConversationState.AWAITING_COMMAND
    return menu_payload


def handle_state_awaiting_product_selection(conversation, message_details):
    """
    Handles user input to find a product. Correctly handles text input and list replies.
    """
    seller = conversation.seller
    
    # --- Part 1: Check for a reply from a list first ---
    interactive_data = message_details.get('interactive', {})
    if interactive_data.get('type') == 'list_reply':
        button_id = interactive_data['list_reply']['id']
        if button_id.startswith('select_product_'):
            try:
                product_id = int(button_id.split('_')[-1])
                product = seller.products.get(id=product_id, is_active=True)
                return _send_product_details_interactive(conversation, product)
            except (ValueError, Product.DoesNotExist):
                return "There was an error with your selection. Please try again."

    # --- Part 2: If not a list selection, process as a text search ---
    message_text = message_details.get('text', {}).get('body', '')
    if not message_text:
        return "Please tell me which product you're interested in, or type 'menu'."

    matching_products = seller.products.filter(name__icontains=message_text, is_active=True)
    product_count = matching_products.count()

    if product_count == 1:
        product = matching_products.first()
        return _send_product_details_interactive(conversation, product)

    elif product_count > 1:
        rows = []
        for product in matching_products[:10]:
            rows.append({
                "id": f"select_product_{product.id}",
                "title": str(product.name)[:24],
                "description": f"${product.price}"[:72]
            })
        
        list_payload = {
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "Multiple Matches Found"},
                "body": {"text": "I found a few items matching your search. Please select one from the list below."},
                "action": {"button": "View Matching Items", "sections": [{"title": "Products", "rows": rows}]}
            }
        }
        
        conversation.state = Conversation.ConversationState.AWAITING_PRODUCT_SELECTION
        return list_payload

    else:
        return "Sorry, I couldn't find any products matching that name. Please try another search or type 'menu'."
    
def handle_state_awaiting_product_action(conversation, message_details):
    """
    Processes the user's action after viewing a product's details.
    Handles 'Add to Cart' or 'Main Menu' button clicks.
    """
    # Check if the payload is from a button click
    if message_details.get('interactive', {}).get('type') == 'button_reply':
        button_id = message_details['interactive']['button_reply']['id']
        print(f"User clicked button with ID: {button_id}")

        if button_id.startswith('add_to_cart_'):
            try:
                product_id = int(button_id.split('_')[-1])
                product = Product.objects.get(id=product_id, seller=conversation.seller)
                conversation.context['viewed_product_id'] = product.id

                if product.sizes:
                    conversation.state = Conversation.ConversationState.AWAITING_SIZE_SELECTION
                    if len(product.sizes) <= 3:
                        buttons = [{"type": "reply", "reply": {"id": f"select_size_{s}", "title": str(s)[:20]}} for s in product.sizes]
                        return {"type": "interactive", "interactive": {"type": "button", "body": {"text": f"Please select a size for the *{product.name}*:"}, "action": {"buttons": buttons}}}
                    else:
                        rows = [{"id": f"select_size_{s}", "title": str(s)[:24]} for s in product.sizes[:10]]
                        return {"type": "interactive", "interactive": {"type": "list", "header": {"type": "text", "text": "Available Sizes"}, "body": {"text": f"Please choose a size for the *{product.name}*:"}, "action": {"button": "View Sizes", "sections": [{"title": "Sizes", "rows": rows}]}}}
                else:
                    conversation.state = Conversation.ConversationState.AWAITING_QUANTITY
                    return "Got it. How many would you like to add?"
            
            except Product.DoesNotExist:
                conversation.state = Conversation.ConversationState.AWAITING_COMMAND
                return "Sorry, that product is no longer available. What else can I help you find?"

        elif button_id == 'show_menu':
             # The global router should catch this, but as a safeguard:
            return handle_state_awaiting_command(conversation, {})

    # Fallback if the user types text instead of using a button
    return "Please use one of the buttons to proceed."

def handle_state_awaiting_size_selection(conversation, message_details):
    """
    Handles the user's reply after being prompted for a size.
    Accepts replies from both button and list interactive messages.
    """
    interactive_data = message_details.get('interactive', {})
    reply_type = interactive_data.get('type') # Will be 'button_reply' or 'list_reply'
    
    # Check if the reply is from a supported interactive type
    if reply_type in ['button_reply', 'list_reply']:
        # The structure for getting the ID is the same for both reply types
        button_id = interactive_data[reply_type]['id']
        
        if button_id.startswith('select_size_'):
            # Extract the size from the ID, removing the 'select_size_' prefix once
            selected_size = button_id.replace('select_size_', '', 1)
            
            # Save the chosen size to the conversation's memory (context)
            conversation.context['selected_size'] = selected_size
            
            # Transition to the next state: asking for quantity
            conversation.state = Conversation.ConversationState.AWAITING_QUANTITY
            return "Got it. How many would you like to add?"
    
    # If the user typed something else or the payload was unexpected
    return "Please select a size from the available options by tapping one of the choices."


def handle_state_awaiting_quantity(conversation, message_details):
    message_text = message_details.get('text', {}).get('body', '')
    try:
        quantity = int(message_text)
        if quantity <= 0:
            return "Please enter a valid quantity (1 or more)."

        product_id = conversation.context.get('viewed_product_id')
        selected_size = conversation.context.get('selected_size')
        
        # This function now returns a dictionary payload
        response_payload = add_item_to_cart(conversation, product_id, quantity, selected_size)

        # Clean up context and reset state
        conversation.context.pop('viewed_product_id', None)
        conversation.context.pop('selected_size', None)
        conversation.state = Conversation.ConversationState.AWAITING_COMMAND
        return response_payload

    except (ValueError, TypeError):
        return "Please enter a valid number for the quantity."
    
def add_item_to_cart(conversation, product_id, quantity, size):
    """
    A helper function that contains the actual database logic for adding an item to the cart.
    NOW RETURNS A DICTIONARY PAYLOAD FOR AN INTERACTIVE MESSAGE.
    """
    try:
        product = Product.objects.get(id=product_id)
        
        cart, _ = Order.objects.get_or_create(
            customer=conversation.customer,
            seller=conversation.seller,
            status=Order.OrderStatus.IN_PROGRESS
        )

        order_item, created = OrderItem.objects.get_or_create(
            order=cart,
            product=product,
            selected_size=size,
            defaults={'price_at_time_of_purchase': product.price}
        )

        if not created:
            order_item.quantity += quantity
        else:
            order_item.quantity = quantity
        
        order_item.save()
        cart.update_total()

        # --- (+) Build the Interactive Message Payload ---
        body_text = (
            f"Great! Added {quantity} x *{product.name}* (Size: {size or 'N/A'}) to your cart.\n\n"
            f"Your cart total is now *${cart.total_amount:.2f}*.\n\n"
            "What would you like to do next?"
        )

        interactive_payload = {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "view_cart", # A clean, reusable ID
                                "title": "View Cart 🛒"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "keep_shopping",
                                "title": "Keep Shopping"
                            }
                        }
                    ]
                }
            }
        }
        return interactive_payload

    except Product.DoesNotExist:
        return "Sorry, an error occurred and I couldn't find that product."
    
def handle_state_viewing_cart(conversation, message_details):
    """
    Displays the cart or processes an action from the cart view.
    """
    button_id = message_details.get('interactive', {}).get('button_reply', {}).get('id')
    
    # --- Part 1: Process a button click from the cart view ---
    if button_id == 'checkout':
        conversation.state = Conversation.ConversationState.AWAITING_DELIVERY_CHOICE
        # IMPORTANT: We call the next handler to generate the next message immediately.
        return handle_state_awaiting_delivery_choice(conversation, {})
    
    # The 'keep_shopping' button is now handled by the global router in process_message

    # --- Part 2: If no button was clicked (or it's a 'view cart' command), DISPLAY the cart ---
    try:
        cart = Order.objects.get(
            customer=conversation.customer,
            seller=conversation.seller,
            status=Order.OrderStatus.IN_PROGRESS
        )
        order_items = cart.items.all()

        if not order_items.exists():
            conversation.state = Conversation.ConversationState.AWAITING_COMMAND
            return "Your shopping cart is currently empty. Type 'menu' to browse products."

        cart_details_list = []
        for item in order_items:
            item_total = item.quantity * item.price_at_time_of_purchase
            size_info = f" (Size: {item.selected_size})" if item.selected_size else ""
            cart_details_list.append(f"- {item.quantity} x {item.product.name}{size_info}: ${item_total:.2f}")
        
        cart_details_text = "\n".join(cart_details_list)
        body_text = (
            f"🛒 *Your Shopping Cart*\n\n"
            f"{cart_details_text}\n\n"
            f"--------------------\n"
            f"*Total: ${cart.total_amount:.2f}*"
        )
        
        interactive_payload = { "type": "interactive", "interactive": {
            "type": "button", "body": {"text": body_text},
            "action": { "buttons": [
                {"type": "reply", "reply": {"id": "checkout", "title": "Proceed to Checkout"}},
                {"type": "reply", "reply": {"id": "keep_shopping", "title": "Add More Items"}},
            ]}
        }}
        conversation.state = Conversation.ConversationState.VIEWING_CART
        return interactive_payload

    except Order.DoesNotExist:
        conversation.state = Conversation.ConversationState.AWAITING_COMMAND
        return "Your shopping cart is currently empty. Type 'menu' to browse products."
    
def handle_state_awaiting_delivery_choice(conversation, message_details):
    """
    Asks the user to choose between delivery and pickup.
    Also processes their button-click response.
    """
    button_id = message_details.get('interactive', {}).get('button_reply', {}).get('id')
    cart = Order.objects.get(customer=conversation.customer, seller=conversation.seller, status=Order.OrderStatus.IN_PROGRESS)
    
    # --- Part 1: Process the user's choice ---
    if button_id == 'select_delivery':
        cart.delivery_option = Order.DeliveryOption.DELIVERY
        cart.save()
        conversation.state = Conversation.ConversationState.AWAITING_DELIVERY_ADDRESS
        return "Great! Please provide your delivery address. You can type a full address or share your location pin."

    elif button_id == 'select_pickup':
        cart.delivery_option = Order.DeliveryOption.PICKUP
        cart.save()
        conversation.state = Conversation.ConversationState.AWAITING_PAYMENT_CONFIRMATION
        return handle_state_awaiting_payment_confirmation(conversation, {})

    # --- Part 2: If no button was clicked, present the options ---
    body_text = "How would you like to receive your order?"
    interactive_payload = {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "select_delivery", "title": "🚚 Delivery"}},
                    {"type": "reply", "reply": {"id": "select_pickup", "title": "🏢 Pickup"}},
                ]
            }
        }
    }
    return interactive_payload

def handle_state_awaiting_delivery_address(conversation, message_details):
    """
    Captures the user's delivery address from either a text or location message.
    """
    cart = Order.objects.get(customer=conversation.customer, seller=conversation.seller, status=Order.OrderStatus.IN_PROGRESS)
    message_type = message_details.get('type')

    address_saved = False
    # Check for a location pin message
    if message_type == 'location':
        location_data = message_details['location']
        lat = location_data['latitude']
        lon = location_data['longitude']
        cart.delivery_location_coordinates = {'latitude': lat, 'longitude': lon}
        # Optionally add address text if Meta provides it
        if location_data.get('address'):
            cart.delivery_address_text = location_data['address']
        cart.save()
        address_saved = True
    
    # Check for a text message
    elif message_type == 'text':
        address_text = message_details['text']['body']
        cart.delivery_address_text = address_text
        cart.save()
        address_saved = True

    if address_saved:
        conversation.state = Conversation.ConversationState.AWAITING_PAYMENT_CONFIRMATION
    # (+) Call the new handler
        return handle_state_awaiting_payment_confirmation(conversation, {})
    else:
        # If the message was not text or location (e.g., an image)
        return "Please provide your address by typing it or sharing your location pin."
    
def handle_state_awaiting_payment_confirmation(conversation, message_details):
    """
    This state is entered right after we decide to trigger an STK push.
    It doesn't process user input, it PERFORMS the payment action.
    """
    try:
        cart = Order.objects.get(
            customer=conversation.customer,
            seller=conversation.seller,
            status=Order.OrderStatus.IN_PROGRESS
        )
        
        # The public URL of our deployed application for the callback
        # We'll create this webhook in a later step
        callback_url = f"https://chapchat-94s8.onrender.com/api/payments/mpesa-callback/"
        
        # Initiate the STK Push
        response = initiate_stk_push(
            phone_number=conversation.customer.phone_number,
            amount=cart.total_amount,
            order_id=cart.id,
            callback_url=callback_url
        )

        if response and response.get('ResponseCode') == '0':
            # STK Push was successfully initiated
            # Update the order status
            cart.status = Order.OrderStatus.PENDING_PAYMENT
            # Store the CheckoutRequestID to link the callback later
            cart.mpesa_checkout_request_id = response.get('CheckoutRequestID') # Requires adding this field to Order model
            cart.save()
            
            return "A payment prompt has been sent to your phone. Please enter your M-Pesa PIN to complete the transaction."
        else:
            # STK push initiation failed
            return "We couldn't initiate the payment request at this time. Please try again shortly by typing 'checkout'."

    except Order.DoesNotExist:
        return "Sorry, I couldn't find your cart to proceed with payment."