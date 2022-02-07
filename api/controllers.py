from email.mime import application
from django.http.response import HttpResponse, JsonResponse
from rest_framework import status

from django.db.utils import OperationalError

from rest_framework.response import Response

from api.logging import ActivityLog
from api.notifications import create_low_quantity_notification

from .reports import HealthAndSafetyReport
from .serializers import UserSerializer,FridgeContentSerializer,ItemSerializer, DoorSerializer, NotificationSerializer
from .models import Door, Notification, Order, User,FridgeContent,Item

from datetime import date, datetime, timedelta
from time import sleep

import os
import json
import threading

class UserController():
    def getAllUsers():
        users = User.objects.all().exclude(is_superuser=True) #exclude superusers (admins) in from the query
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    def singleUserCheck(pk):
        # Check to see if user exists
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist: #check if the user exists
            response = {
                "error": "user does not exist, please update user list for correct list of users"
            }
            return JsonResponse(response, status=status.HTTP_404_NOT_FOUND) # Return 404
        # Check to see if user is admin i.e. superuser
        if user.is_superuser == True:
            response = {
                "error": "This user is an admin, you cannot change their information"
            }
            return JsonResponse(status=status.HTTP_403_FORBIDDEN) # Return 403
        return None

    #get a single user from a primary key
    def getSingleUser(pk):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

    #update a single user with primary key pk with the contents of requests
    def updateSingleUser(request,pk):
        user = User.objects.get(id=pk)
        serializer = UserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FridgeContentController():
    #returns all fridge content
    def getAllFridgeContent():
        fridge_contents = FridgeContent.objects.all()
        serializer = FridgeContentSerializer(fridge_contents, many=True)
        return Response(serializer.data)

    def getRecentlyAddedFridgeContent():
        return FridgeContent.objects.filter(introduction_date=datetime.now())

    def getCurrentFridgeVolumePercentage():
        volumePercentage = (FridgeContentController.getCurrentFridgeVolume() / 400) * 100
        response = {
            "percentage": volumePercentage
        }
        return Response(response)

    def getCurrentFridgeVolume():
        fridge_contents = FridgeContent.objects.all()
        current_volume = 0
        for content in fridge_contents:
            current_volume += content.item.weight * content.current_quantity
        return current_volume

    def checkFridgeOverfill(new_volume):
        current_volume = FridgeContentController.getCurrentFridgeVolume()
        if current_volume + new_volume > 400:
            return True
        return False
    # Check to see if fridge content exists
    def singleFridgeContentCreateCheck(pk): 
        try:
            content = FridgeContent.objects.get(id=pk)
        except FridgeContent.DoesNotExist:
            response = {
                "error": "fridge content does not exist, please update list of fridge content"
            }
            return JsonResponse(response, status=status.HTTP_404_NOT_FOUND) # Return 404
        return None

    def createFridgeContent(request):
        serializer = FridgeContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            try:
                content = FridgeContent.objects.get(id=serializer.data.get("id"))
                t = threading.Thread(target=ActivityLog.writeNewFridgeContentActivityToLog,args=[content], daemon=True)
                t.start()
            except (OperationalError, KeyError):
                print("unable to write log")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def updateQuantity(request,pk):
        try:
            content = FridgeContent.objects.get(id=pk)
        except FridgeContent.DoesNotExist:
            return JsonResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
        old_quantity = content.current_quantity
        last_inserted_by = request.user.id
        print(request.data["current_quantity"])
        data = {
            "current_quantity": request.data["current_quantity"],
            "last_inserted_by": last_inserted_by
        }
        serializer = FridgeContentSerializer(instance=content, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            t = threading.Thread(target=ActivityLog.writeUpdateFridgeContentActivityToLog,args=[content, old_quantity], daemon=True)
            t.start()
            t2 = threading.Thread(target=create_low_quantity_notification, args=[content], daemon=True)
            t2.start()
            return Response(serializer.data) #TODO: return current quantity
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ItemController():
    #get all items
    def getAllItems():
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
    #get item from barcode
    def getItemFromBarcode(barcode):
        try:
            item = Item.objects.get(barcode=barcode)
            serializer = ItemSerializer(item, many=False)
            return Response(serializer.data)
        except Item.DoesNotExist:
            response = {
                "error": "The item you have scanned does not exist within the system, it will need to be added manually"
            }
            return JsonResponse(response, status=status.HTTP_404_NOT_FOUND)
    #create item from request
    def createItem(request):
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportController():
    #REPORT_PATH = "./reports/"
    def getAllReportInfo():
        all_report_info = []
        directory = os.fsencode("reports/")
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".xlsx"):
                #get full path of file
                file_path = os.path.join("reports/", filename)
                file_size = os.path.getsize(file_path)
                #get creation time as timestamp then convert to dd-MM-yy
                creation_date = os.path.getmtime(file_path)
                creation_date = datetime.fromtimestamp(creation_date).strftime('%d-%m-%Y')
                report_info = {
                    "name": filename,
                    "size": file_size,
                    "creation_date": creation_date
                }
                all_report_info.append(report_info)
        all_report_info = json.dumps({'reports_info': all_report_info}, indent=4)
        return HttpResponse(all_report_info, content_type="application/json")
    
    def getNewReport():
        return HealthAndSafetyReport.generateReport()
    
    def getReport(filename):
        file_path = os.path.join("reports/", filename)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
        else:
            response = {
                "error": "report does not exist or has been deleted, please refresh report page or contact system admin"
            }
            return JsonResponse(response, status=status.HTTP_404_NOT_FOUND)

class DoorController():
    FRONT_DOOR = "Front Door"
    BACK_DOOR = "Back Door"

    #Auto lock door after 31 seconds (extra second to give for response time)
    def autoLockDoor(name):
        sleep(31)
        status = -1
        # attempt tolock door until successful
        while status != 200:  
            if name == DoorController.FRONT_DOOR:
                response = DoorController.lockFrontDoor()
                status = response.status_code
            else:
                response = DoorController.lockBackDoor()
                status = response.status_code

    def getDoorStatus(name):
        door = Door.objects.get(name=name)
        return door.door_locked

    def setDoorStatus(name, status):
        door = Door.objects.get(name=name)
        serializer = DoorSerializer(instance=door, data={"door_locked": status}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def unlockFrontDoor():
        front_door_locked = DoorController.getDoorStatus(DoorController.FRONT_DOOR)
        back_door_locked = DoorController.getDoorStatus(DoorController.BACK_DOOR)
        if front_door_locked and back_door_locked:
            return DoorController.setDoorStatus(DoorController.FRONT_DOOR, False)
        response = {
            "error": "either front door is already unlocked or back door is unlocked, please refresh page to see."
        }
        return JsonResponse(response, status=status.HTTP_403_FORBIDDEN) #TODO: Check if right error code

    def unlockBackDoor():
        front_door_locked = DoorController.getDoorStatus(DoorController.FRONT_DOOR)
        back_door_locked = DoorController.getDoorStatus(DoorController.BACK_DOOR)
        if front_door_locked and back_door_locked:
           return DoorController.setDoorStatus(DoorController.BACK_DOOR, False)
        response = {
            "error": "either front door is already unlocked or back door is unlocked, please refresh page to see."
        }
        return JsonResponse(status=status.HTTP_403_FORBIDDEN) #TODO: Check if right error code

    def lockFrontDoor():
        front_door_locked = DoorController.getDoorStatus(DoorController.FRONT_DOOR)
        if not front_door_locked:
            return DoorController.setDoorStatus(DoorController.FRONT_DOOR, True)
        response = {
            "error": "front door is already locked, please refresh page to see."
        }
        return JsonResponse(response, status=status.HTTP_403_FORBIDDEN) #TODO: Check if right error code

    def lockBackDoor():
        back_door_locked = DoorController.getDoorStatus(DoorController.BACK_DOOR)
        if not back_door_locked:
            return DoorController.setDoorStatus(DoorController.BACK_DOOR, True)
        response = {
            "error": "front door is already locked, please refresh page to see."
        }
        return JsonResponse(response, status=status.HTTP_403_FORBIDDEN) #TODO: Check if right error code

    def returnAllDoorStatus(request):
        doors = Door.objects.all()
        serializer = DoorSerializer(doors, many=True)
        return Response(serializer.data)

class ActivityLogController():
    def getLatestLogs():
        logs = []
        week_ago = datetime.now() - timedelta(days=7)
        directory = os.fsencode(ActivityLog.LOG_PATH)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename == "test_log.txt":
                continue
            file_path = os.path.join(ActivityLog.LOG_PATH, filename)
            creation_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            #Check to see if logs are from within the last week
            if creation_date > week_ago:
                creation_date = creation_date.strftime('%d-%m-%Y')
                log_info = {
                    "name": filename,
                    "creation_date": creation_date
                }
                logs.append(log_info)
        logs = json.dumps({'logs': logs}, indent=4)
        return HttpResponse(logs, content_type="application/json")

    def downloadLog(filename):
        #read in contents of the log file and return as a text file TODO: see if filetype needs changing
        file_path = os.path.join(ActivityLog.LOG_PATH, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as fh:
                response = HttpResponse(fh.read(), content_type = "text/plain")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
        else:
            response = {
                "error": "log has been deleted or does not exist, please refresh log page or contact system admin"
            }
            return JsonResponse(response, status=status.HTTP_404_NOT_FOUND)

class NotificationController():
    def getAllNotifications(request):
        notifications = Notification.objects.all().order_by('-creation_date')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def deleteNotification(request, pk):
        try:
            notification = Notification.objects.get(id=pk)
        except Notification.DoesNotExist:
            response = {
                "error": "notification may already have been deleted"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        success = notification.delete()
        response = {}
        if success:
            response["success"] = "deleted notification successfully"
            return Response(response)
        else:
            response["error"] = "error deleting notification"
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderController():
    def getAllOrders():
        orders = Order.objects.all()
        order_list = []
        for order in orders:
            order_dict = {}
            order_dict['id'] = order.id
            order_dict["delivered"] = order.delivered
            order_items = []
            for order_item in order.order_items.all():
                order_item_details = {
                    "item": order_item.item.name,
                    "quantity": order_item.quantity
                }
                order_items.append(order_item_details)
            order_dict['order_items'] = order_items
            order_list.append(order_dict)
        
        order_list = json.dumps(order_list, indent=4)
        return HttpResponse(order_list, content_type="application/json")

    def getUserOrders(pk):
        orders = Order.objects.filter(delivery_driver=pk)
        order_list = []
        for order in orders:
            order_dict = {}
            order_dict['id'] = order.id
            order_dict["delivered"] = order.delivered
            order_items = []
            for order_item in order.order_items.all():
                order_item_details = {
                    "item": order_item.item.name,
                    "quantity": order_item.quantity
                }
                order_items.append(order_item_details)
            order_dict['order_items'] = order_items
            order_list.append(order_dict)
        
        order_list = json.dumps(order_list, indent=4)
        return HttpResponse(order_list, content_type="application/json")

    def updateDelivered(pk):
        new_fridge_contents = FridgeContentController.getRecentlyAddedFridgeContent()
        if new_fridge_contents == None:
            response = {
                "error": "Nothing has been added to the fridge today, please add items first"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            response = {
                "error": "order does not exist, please update order list for correct list of orders"
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        for order_item in order.order_items.all():
            item_found = False
            print(f'order item name: {order_item.item.name}')
            for fridge_content in new_fridge_contents:
                print(f'fridge content item name: {fridge_content.item.name}')
                if order_item.item.name == fridge_content.item.name and order_item.quantity == fridge_content.default_quantity:
                    item_found = True
            if item_found == False:
                response = {
                    "error": f'{order_item.item.name} has not been added to the fridge, order cannot be completed'
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        order.delivered = True
        order.save()
        response = {
            "success": "order delivered successfully"
        }
        return Response(response)

        
