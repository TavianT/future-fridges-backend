from datetime import datetime,timedelta
from django.utils.timezone import make_aware

from .models import FridgeContent

def create_low_quantity_notification():
    return None

def create_expiring_items_notification():
    three_days_from_now = datetime.now() + timedelta(days=3)
    aware_date = make_aware(three_days_from_now)
    #Get all items in fridge expiring within 3 days
    fridge_contents = FridgeContent.objects.all().filter(expiration_date__lt=aware_date)
    message = 'The following items will be expiring soon:\n'
    for fridge_content in fridge_contents:
        fcStr = f'{fridge_content}'