from django.http.response import HttpResponse
from .models import Item, FridgeContent
from django.utils.timezone import make_aware

import xlsxwriter
from datetime import datetime
import json

class HealthAndSafetyReport():
    def generateReport():
        headers = ['Item name', 'introduction date', 'expiration date', 'quantity remaining']
        creation_datetime = datetime.now().strftime('%d%m%Y%H%M%S')
        aware_date = make_aware(datetime.now())
        report_name = f'health_and_safety_report.{creation_datetime}.xlsx'
        fridge_contents = FridgeContent.objects.all().filter(expiration_date__lt=aware_date)
        workbook = xlsxwriter.Workbook(f'reports/{report_name}')
        date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'left'})
        worksheet = workbook.add_worksheet()

        row = 1
        col = 0

        for header in headers:
            worksheet.write(0, col, header)
            col += 1
        col = 0

        for obj in fridge_contents:
            worksheet.write(row, col, obj.item.name)
            col += 1
            worksheet.write_datetime(row,col,obj.introduction_date, date_format) #TODO: convert to DD/MM/YYYY
            col += 1
            worksheet.write_datetime(row,col,obj.expiration_date, date_format) #TODO: convert to DD/MM/YYYY
            col += 1
            worksheet.write(row, col, obj.quantity)
            col = 0
            row += 1
        workbook.close()
        response = json.dumps({"name": report_name}, indent=4)
        return HttpResponse(response, content_type="application/json")

        
