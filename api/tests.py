from time import sleep
from django.http import response
from django.test.testcases import SerializeMixin
from rest_framework import status
from rest_framework.test import APITestCase

from api.logging import ActivityLog
from .models import Door, Supplier,Item,FridgeContent,User
from django.urls import reverse
from datetime import datetime, timedelta
import os

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


class DoorTests(APITestCase):
    def setUp(self):
        self.test_dd_user = User.objects.create(email= "tester@test.com", name="Test Boi", role="DD", fridge_access=True)
        self.test_hc_user = User.objects.create(email= "tester8@test2.com", name="Test Girl", role="HC", fridge_access=True)
        self.test_user_no_access = User.objects.create(email= "testa@test.com", name="Test Person", role="C", fridge_access=False)
        
        #Front and Back door entities are created when server is ran so no need to create them here

    def testFrontDoorUnlock(self):
        url = reverse('unlock-door')
        self.client.force_login(self.test_hc_user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Door.objects.get(name='Front Door').door_locked)

    def testBackDoorUnlock(self):
        url = reverse('unlock-door')
        self.client.force_login(self.test_dd_user)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Door.objects.get(name='Back Door').door_locked)
    
    def testUnauthorisedDoorUnlock(self):
        url = reverse('unlock-door')
        self.client.force_login(self.test_user_no_access)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Door.objects.get(name='Front Door').door_locked)
    
    def testFrontDoorLock(self):
        front_door =  Door.objects.get(name='Front Door')
        front_door.door_locked = False
        front_door.save()
        self.client.force_login(self.test_hc_user)
        url = reverse('lock-door')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Door.objects.get(name='Front Door').door_locked)
    
    def testBackDoorLock(self):
        back_door =  Door.objects.get(name='Back Door')
        back_door.door_locked = False
        back_door.save()
        self.client.force_login(self.test_dd_user)
        url = reverse('lock-door')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Door.objects.get(name='Front Door').door_locked)

class ActivityLogTests(APITestCase):
    def setUp(self):
        self.week_from_today = datetime.now() + timedelta(days=7)
        self.week_ago = datetime.now() - timedelta(days=7)
        self.test_supplier = Supplier.objects.create(name="supplier of tests", address="101 Test Street", contact_number="07878371993", email="test@food.com")
        self.test_item = Item.objects.create(name="Chicken", weight=166, barcode="010101205647", supplier=self.test_supplier)
        self.test_item_2 = Item.objects.create(name="Carrot", weight=0.1, barcode="010101205010", supplier=self.test_supplier)
        self.test_user = User.objects.create(email= "tester@test.com", name="Test Boi", role="DD", fridge_access=True)
        self.test_fridge_content = FridgeContent.objects.create(item=self.test_item, quantity=4, expiration_date=self.week_from_today, last_inserted_by=self.test_user)
        self.test_fridge_content_2 = FridgeContent.objects.create(item=self.test_item_2, quantity=22, expiration_date=self.week_ago, last_inserted_by=self.test_user)
    
    def testActivityLogWriteNewContent(self):
        ActivityLog.writeNewFridgeContentActivityToLog(self.test_fridge_content)
        current_date = datetime.now().strftime('%d_%m_%Y')
        correct_file_name = f'activity_log_{current_date}.txt'

        correct_file_path = os.path.join(ActivityLog.LOG_PATH, correct_file_name)

        self.assertTrue(os.path.exists(correct_file_path))

    def testActivityLogUpdateContent(self):
        ActivityLog.writeUpdateFridgeContentActivityToLog(self.test_fridge_content_2, 20)
        current_date = datetime.now().strftime('%d_%m_%Y')
        correct_file_name = f'activity_log_{current_date}.txt'
        correct_file_path = os.path.join(ActivityLog.LOG_PATH, correct_file_name)

        self.assertTrue(os.path.exists(correct_file_path))

    def testGetAllLogsNames(self):
        log_in_response = False
        current_date = datetime.now().strftime('%d_%m_%Y')
        correct_file_name = f'activity_log_{current_date}.txt'
        url = reverse('logs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for log in response.json()["logs"]:
            if log["name"] == correct_file_name:
                log_in_response = True
        
        self.assertTrue(log_in_response)

    def testGetCurrentLog(self):
        current_date = datetime.now().strftime('%d_%m_%Y')
        correct_file_name = f'activity_log_{current_date}.txt'

        url = reverse('download-log', args=[correct_file_name])
        response = self.client.get(url)

        self.assertEquals(
            response.get('Content-Disposition'),
            f'attachment; filename={correct_file_name}'
        )