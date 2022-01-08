from django.http import response
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Supplier,Item,FridgeContent,User
from django.urls import reverse
from datetime import datetime, timedelta

class ItemTests(APITestCase):
    def setUp(self):
        self.test_supplier = Supplier.objects.create(name="supplier of tests", address="101 Test Street", contact_number="07878371993", email="test@food.com")
        self.test_item = Item.objects.create(name="Chicken", weight=166, barcode="010101205647", supplier=self.test_supplier)
    
    def test_item_read_from_barcode(self):
        url = reverse('item-barcode',args=[self.test_item.barcode])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'],'Chicken')

    def test_item_create(self):
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

    def test_get_all_items_test(self):
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

    def test_get_all_fridge_contents(self):
        url = reverse('fridge-contents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["quantity"],4)

    def test_create_fridge_content(self):
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

    def test_update_fridge_content_quantity(self):
        url = reverse('update-quantity',args=[self.test_fridge_content.id]) #id of self.test_fridge_content
        data = {
            "quantity": 2
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FridgeContent.objects.get(id=1).quantity, data["quantity"])



    


