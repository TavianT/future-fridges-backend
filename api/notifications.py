from datetime import datetime,timedelta
from email import message
from time import sleep
from django.utils.timezone import make_aware

from .models import FridgeContent, Notification, User
from constance import config
from django.core.mail import send_mail

def create_low_quantity_notification(fridge_content):
    if fridge_content.current_quantity / fridge_content.default_quantity <= 0.2:
        message = f'{fridge_content.item.name} is low on stock, only {fridge_content.current_quantity} remaining'
        head_chefs = User.objects.all().filter(role='HC')
        notification = Notification.objects.create(message=message)
        notification.save()
        for head_chef in head_chefs:
            notification.recipients.add(head_chef)
        send_notification_email(notification)

def create_expiring_items_notification():
    three_days_from_now = datetime.now() + timedelta(days=3)
    aware_date = make_aware(three_days_from_now)
    #Get all items in fridge expiring within 3 days
    fridge_contents = FridgeContent.objects.all().filter(expiration_date__lt=aware_date)
    message = 'The following items have expired or will be expiring within the next 3 days:\n'
    for fridge_content in fridge_contents:
        fcStr = f'{fridge_content.item.name} - {fridge_content.expiration_date}\n'
        message += fcStr
    head_chefs = User.objects.all().filter(role='HC')
    notification = Notification.objects.create(message=message)
    notification.save()
    for head_chef in head_chefs:
        notification.recipients.add(head_chef)
    send_notification_email(notification)
    sleep(86400) # 1 Day

def send_notification_email(notification):
    if notification.delivered == False:
        email_list = []
        for recipient in notification.recipients.all():
            email_list.append(recipient.email)
        send_mail(
            subject='Future Fridges Notification',
            message=notification.message,
            from_email=config.BUSINESS_EMAIL_ADDRESS,
            recipient_list=email_list,
            auth_user=config.BUSINESS_EMAIL_ADDRESS,
            auth_password=config.BUSINESS_EMAIL_PASSWORD
        )
        notification.delivered=True
