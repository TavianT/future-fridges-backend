from django.http import response
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Supplier,Item,FridgeContent,User
from django.urls import reverse

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

    
# class FridgeCotentTests(APITestCase):
#     def setUp(self):
#         self.test_supplier = Supplier.objects.create(name="supplier of tests", address="101 Test Street", contact_number="07878371993", email="test@food.com")
#         self.test_item = Item.objects.create(name="Chicken", weight=166, barcode="010101205647", supplier=self.test_supplier)
#         self.test_user = User.objects.create(name="Test Boi", )
#         self.test_fridge_content = FridgeContent.objects.create()

    


