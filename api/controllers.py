from django.http.response import HttpResponse, JsonResponse
from rest_framework import status

from django.db.utils import OperationalError

from rest_framework.response import Response

from api.logging import ActivityLog
from api.notifications import create_low_quantity_notification

from .reports import HealthAndSafetyReport
from .serializers import UserSerializer,FridgeContentSerializer,ItemSerializer, DoorSerializer, NotificationSerializer
from .models import Door, Notification, User,FridgeContent,Item

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
            return HttpResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
        # Check to see if user is admin i.e. superuser
        if user.is_superuser == True:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN) # Return 403
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

    def checkFridgeOverfill(new_volume):
        fridge_contents = FridgeContent.objects.all()
        current_volume = 0
        for content in fridge_contents:
            current_volume += content.item.weight * content.current_quantity
        if current_volume + new_volume > 400:
            return True
        return False
    # Check to see if fridge content exists
    def singleFridgeContentCreateCheck(pk): 
        try:
            content = FridgeContent.objects.get(id=pk)
        except FridgeContent.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
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
            return HttpResponse(status=status.HTTP_404_NOT_FOUND) # Return 404
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
        print(serializer.errors)
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
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
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
        #convert all_report_info into json array object
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
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

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
        return HttpResponse(status=status.HTTP_403_FORBIDDEN) #TODO: Check if right error code

    def unlockBackDoor():
        front_door_locked = DoorController.getDoorStatus(DoorController.FRONT_DOOR)
        back_door_locked = DoorController.getDoorStatus(DoorController.BACK_DOOR)
        if front_door_locked and back_door_locked:
           return DoorController.setDoorStatus(DoorController.BACK_DOOR, False)
        return HttpResponse(status=status.HTTP_403_FORBIDDEN) #TODO: Check if right error code

    def lockFrontDoor():
        front_door_locked = DoorController.getDoorStatus(DoorController.FRONT_DOOR)
        if not front_door_locked:
            return DoorController.setDoorStatus(DoorController.FRONT_DOOR, True)
        return HttpResponse(status=status.HTTP_403_FORBIDDEN) #TODO: Check if right error code

    def lockBackDoor():
        back_door_locked = DoorController.getDoorStatus(DoorController.BACK_DOOR)
        if not back_door_locked:
            return DoorController.setDoorStatus(DoorController.BACK_DOOR, True)
        return HttpResponse(status=status.HTTP_403_FORBIDDEN) #TODO: Check if right error code

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
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

class NotificationController():
    def getAllNotifications(request):
        notifications = Notification.objects.all().order_by('-creation_date')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def deleteNotification(request, pk):
        try:
            notification = Notification.objects.get(id=pk)
        except Notification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        success = notification.delete()
        data = {}
        if success:
            data["success"] = "deleted notification successfully"
            return Response(data)
        else:
            data["error"] = "error deleting notification"
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
