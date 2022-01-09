from datetime import date

from api.models import FridgeContent
from enum import Enum
from time import sleep

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
                print("Reordering food")
                content_to_reorder = FridgeContent.objects.all().filter(current_quantity__lte=0)
                for supplier in content_to_reorder.item.supplier:
                    reorder_str = ''
                    for content in content_to_reorder:
                        if supplier == content.item.supplier:
                            reorder_str += f'Item name: {content.item.name}\nBarcode: {content.item.barcode}\nQuantity (units to reorder): {content.default_quantity}\n\n\n'
                    
                    
                            
            else:
                sleep(86400) # 1 Day


