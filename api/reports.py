from django.http.response import HttpResponse
from .models import Item, FridgeContent
from django.utils.timezone import make_aware

import xlsxwriter
from datetime import datetime
import json
import os

class HealthAndSafetyReport():
    def generateReport():
        #Headers of the spreadsheet
        headers = ['Item name', 'introduction date', 'expiration date', 'quantity remaining']
        creation_datetime = datetime.now().strftime('%d%m%Y%H%M%S')
        #Make the date aware i.e. add a timezone
        aware_date = make_aware(datetime.now())
        report_name = f'health_and_safety_report.{creation_datetime}.xlsx'
        #Check for expired items
        fridge_contents = FridgeContent.objects.all().filter(expiration_date__lt=aware_date).order_by('expiration_date')
        workbook = xlsxwriter.Workbook(f'reports/{report_name}')
        #Add format dd/mm/yy format to workboot
        date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'left'})
        worksheet = workbook.add_worksheet()

        row = 1
        col = 0
        #add headers to workbook
        for header in headers:
            worksheet.write(0, col, header)
            col += 1
        col = 0

        #Add data to workbook
        for obj in fridge_contents:
            worksheet.write(row, col, obj.item.name)
            col += 1
            worksheet.write_datetime(row,col,obj.introduction_date, date_format)
            col += 1
            worksheet.write_datetime(row,col,obj.expiration_date, date_format)
            col += 1
            worksheet.write(row, col, obj.current_quantity)
            col = 0
            row += 1
        workbook.close()
        file_path = os.path.join("reports/", report_name)
        file_size = os.path.getsize(file_path)
        creation_date = os.path.getmtime(file_path)
        creation_date = datetime.fromtimestamp(creation_date).strftime('%d-%m-%Y')
        report = {
            "name": report_name,
            "size": file_size,
            "creation_date": creation_date
            }
        response = json.dumps(report, indent=4)
        return HttpResponse(response, content_type="application/json")

        
