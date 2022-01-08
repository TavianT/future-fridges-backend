from time import sleep
from django.http import response
from django.test.testcases import SerializeMixin
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Supplier,Item,FridgeContent,User
from django.urls import reverse
from datetime import datetime, timedelta

class ItemTests(APITestCase):
    def setUp(self):
        self.test_supplier = Supplier.objects.create(name="supplier of tests", address="101 Test Street", contact_number="07878371993", email="test@food.com")
        self.test_item = Item.objects.create(name="Chicken", weight=166, barcode="010101205647", supplier=self.test_supplier)
    
    def testItemReadFromBarcode(self):
        url = reverse('item-barcode',args=[self.test_item.barcode])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'],'Chicken')

    def testItemCreate(self):
        url = reverse('create-item')
        data = {
            "name": "Spinach",
            "weight": 22,
            "barcode": "111111111111",
            "supplier": 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Item.objects.count(), 2) #This item and item created in setup
        self.assertEqual(Item.objects.get(barcode=data["barcode"]).name, data["name"])

    def testGetAllItemsTest(self):
        url = reverse('items')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"],"Chicken")

    
class FridgeContentTests(APITestCase):
    def setUp(self):
        self.week_from_today = datetime.now() + timedelta(days=7)
        self.test_supplier = Supplier.objects.create(name="supplier of tests", address="101 Test Street", contact_number="07878371993", email="test@food.com")
        self.test_item = Item.objects.create(name="Chicken", weight=166, barcode="010101205647", supplier=self.test_supplier)
        self.test_user = User.objects.create(email= "tester@test.com", name="Test Boi", role="DD", fridge_access=True)
        self.test_fridge_content = FridgeContent.objects.create(item=self.test_item, quantity=4, expiration_date=self.week_from_today, last_inserted_by=self.test_user)

    def testGetAllFridgeContents(self):
        url = reverse('fridge-contents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["quantity"],4)

    def testCreateFridgeContent(self):
        url = reverse('create-fridge-content')
        data = {
            "item": 1,
            "quantity": 16,
            "expiration_date": "2022-02-01",
            "last_inserted_by": 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FridgeContent.objects.count(), 2) #This cotent and content created in setup

    def testUpdateFridgeContentQuantity(self):
        url = reverse('update-quantity',args=[self.test_fridge_content.id]) #id of self.test_fridge_content
        data = {
            "quantity": 2
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FridgeContent.objects.get(id=1).quantity, data["quantity"])

#Allows report tests to be ran in serial
class ReportTestMixin(SerializeMixin):
    lockfile = __file__

class ReportTests(ReportTestMixin,APITestCase):
    def setUp(self):
        self.file_type = ".xlsx"
        self.week_from_today = datetime.now() + timedelta(days=7)
        self.week_ago = datetime.now() - timedelta(days=7)
        self.test_supplier = Supplier.objects.create(name="supplier of tests", address="101 Test Street", contact_number="07878371993", email="test@food.com")
        self.test_item = Item.objects.create(name="Chicken", weight=166, barcode="010101205647", supplier=self.test_supplier)
        self.test_item_2 = Item.objects.create(name="Carrot", weight=0.1, barcode="010101205010", supplier=self.test_supplier)
        self.test_user = User.objects.create(email= "tester@test.com", name="Test Boi", role="DD", fridge_access=True)
        self.test_fridge_content = FridgeContent.objects.create(item=self.test_item, quantity=4, expiration_date=self.week_from_today, last_inserted_by=self.test_user)
        self.test_fridge_content_2 = FridgeContent.objects.create(item=self.test_item_2, quantity=22, expiration_date=self.week_ago, last_inserted_by=self.test_user)

    def testReportGeneration(self):
        url = reverse('generate-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"].endswith(self.file_type),True)

    def testGetAllReports(self):
        url = reverse('all-reports')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['reports_info'][0]["name"].endswith(self.file_type),True)

    def testGetReport(self):
        url = reverse('donwload-report', args=["test_report.xlsx"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #TODO: Figure out how to read contents of file


