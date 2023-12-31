from datetime import date

from api.models import FridgeContent, Order, OrderItem, User
from enum import Enum
from time import sleep
from constance import config
from django.core.mail import send_mail

class Dates(Enum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6


class Reorder():

    def run(reorder_date):
        while True:
            if date.today().weekday() == reorder_date: #if today is monday
                order = Order.objects.create(delivery_driver=User.objects.get(role='DD'))
                print("Reordering food")
                content_to_reorder = FridgeContent.objects.all().filter(current_quantity__lte=0)
                suppliers = []
                for content in content_to_reorder:
                    if content.item.supplier not in suppliers:
                        suppliers.append(content.item.supplier)
                    
                    order_item_exists = OrderItem.objects.filter(item = content.item, quantity=content.default_quantity).exists()
                    if order_item_exists:
                        print(f'order item exists')
                        order_item = OrderItem.objects.filter(item = content.item, quantity=content.default_quantity).first()
                        order.order_items.add(order_item)
                    else:
                        order_item = OrderItem.objects.create(item = content.item, quantity=content.default_quantity)
                        order_item.save()
                        order.order_items.add(order_item)

                order.save()
                
                for supplier in suppliers:
                    reorder_str = '' #TODO: Add business name
                    for content in content_to_reorder:
                        if supplier.name == content.item.supplier.name:
                            reorder_str += f'Item name: {content.item.name}\nBarcode: {content.item.barcode}\nQuantity (units to reorder): {content.default_quantity}\n\n'
                            content.delete()
                    reorder_str += f'Please send the order to:\n{config.BUSINESS_ADDRESS}\n'
                    reorder_str += f'If there are any issues or questions please call {config.BUSINESS_CONTACT_NUMBER} or respond to this email'
                    print(reorder_str)

                    #Send Email
                    success = send_mail(
                        subject='Reorder items below',
                        message=reorder_str,
                        from_email=config.BUSINESS_EMAIL_ADDRESS,
                        recipient_list=[supplier.email],
                        auth_user=config.BUSINESS_EMAIL_ADDRESS,
                        auth_password=config.BUSINESS_EMAIL_PASSWORD
                    )
                    print(f'success = {success}')
                    #TODO: send notification if successful
                
                content_to_reorder.delete()
                sleep(86400) # 1 Day 
                    
                            
            else:
                print("Try again tomorrow")
                sleep(86400) # 1 Day


