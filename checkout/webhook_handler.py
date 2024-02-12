from django.http import HttpResponse
from .models import Order, OrderLineItem
from products.models import Product
import json
import time
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle a generic/unknown/unexpected webhook event"""
        return HttpResponse(content=f'Unhandled webhook received: {event["type"]}', status=200)

    def handle_payment_intent_succeeded(self, event):
        """Handle the payment_intent.succeeded webhook from Stripe"""
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # Retrieve the Charge object
        stripe_charge = stripe.Charge.retrieve(intent.latest_charge)
        billing_details = stripe_charge.billing_details
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)

        # Clean data in the shipping details
        if shipping_details:
            for field, value in shipping_details.address.items():
                if value == "":
                    shipping_details.address[field] = None

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            return HttpResponse(content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database', status=200)
        
        try:
            order = Order.objects.create(
                full_name=shipping_details.name if shipping_details else 'Anonymous',
                email=billing_details.email,
                phone_number=shipping_details.phone if shipping_details else '',
                country=shipping_details.address.country if shipping_details else '',
                postcode=shipping_details.address.postal_code if shipping_details else '',
                town_or_city=shipping_details.address.city if shipping_details else '',
                street_address1=shipping_details.address.line1 if shipping_details else '',
                street_address2=shipping_details.address.line2 if shipping_details else '',
                county=shipping_details.address.state if shipping_details else '',
                grand_total=grand_total,
                original_bag=bag,
                stripe_pid=pid,
            )
            for item_id, item_data in json.loads(bag).items():
                product = Product.objects.get(id=item_id)
                if isinstance(item_data, int):
                    OrderLineItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data,
                    )
                else:
                    for size, quantity in item_data['items_by_size'].items():
                        OrderLineItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            product_size=size,
                        )
            return HttpResponse(content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook', status=200)
        except Exception as e:
            if order:
                order.delete()
            return HttpResponse(content=f'Webhook received: {event["type"]} | ERROR: {e}', status=500)

    def handle_payment_intent_payment_failed(self, event):
        """Handle the payment_intent.payment_failed webhook from Stripe"""
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)

