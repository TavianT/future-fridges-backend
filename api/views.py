import re
import threading
from django.http.response import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status

from rest_framework.decorators import api_view
import api

from api.logging import ActivityLog
from api.models import Item, Order
from .controllers import ActivityLogController, DoorController, NotificationController, OrderController, ReportController, UserController, FridgeContentController, ItemController, OrderItemController
from .serializers import UserSerializer

'''Auth function'''
#Used to login to the app via the backend, user information is saved as an instace and can be accessed without needing to pass any information about the current user
@csrf_exempt
@require_http_methods(["POST"])
def userLogin(request):
    #Takes data from form via GET request
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, username=email, password=password)
    if user is not None: #if login successful
        login(request, user)
        serializer = UserSerializer(user, many=False)
        return JsonResponse(serializer.data)
    else:
        response = {
            "error": "invalid email address or password"
        }
        return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED) #return 401

#Logs the user out and clears instance
@csrf_exempt
@require_http_methods(["GET"])
def userLogout(request):
    logout(request)
    return HttpResponse(status=status.HTTP_200_OK)


'''User endpoint functions'''
#Get all users who are not superusers (admins)
@api_view(['GET'])
def allUsers(request):
    return UserController.getAllUsers()

@api_view(['GET', 'PUT'])
def singleUser(request, pk):
    error = UserController.singleUserCheck(pk) #Checks to see if user exists and is not a superuser (admin)
    if error is None:
        # Return user model
        if request.method == 'GET':
            return UserController.getSingleUser(pk)
        # Update included fields
        if request.method == 'PUT':
            return UserController.updateSingleUser(request,pk)
    return error

@api_view(['GET'])
def allDeliveryDrivers(request):
    return UserController.getDeliveryDrivers()

'''Fridge Content functions'''

@api_view(['GET'])
#return all contents of the fridge
def allFridgeContent(request):
    return FridgeContentController.getAllFridgeContent()

@api_view(['GET'])
def recentFridgeContent(request):
    return FridgeContentController.getRecentFridgeContent()

@api_view(['POST'])
def createFridgeContent(request):
    item = Item.objects.get(id=request.data["item"])
    #Check if adding this item will overfill the fridge
    if FridgeContentController.checkFridgeOverfill(item.weight * float(request.data["current_quantity"])):
        response = {
            "error": "Adding this item will overfill the fridge, please speak to a member of staff to fix the issue"
        }
        return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
    return FridgeContentController.createFridgeContent(request)

@api_view(['PUT'])
def updateContentQuantity(request,pk):
    error = FridgeContentController.singleFridgeContentCreateCheck(pk)
    if error is None:
        return FridgeContentController.updateQuantity(request,pk)
    return error

@api_view(['GET'])
def getVolumePercentage(request):
    return FridgeContentController.getCurrentFridgeVolumePercentage()           

'''Item functions'''
@api_view(['GET'])
def allItems(request):
    return ItemController.getAllItems()
#Get contents of item model from a barcode
@api_view(['GET'])
def singleItemFromBarcode(request, barcode):
    return ItemController.getItemFromBarcode(barcode)

@api_view(['POST'])
def createItem(request):
    return ItemController.createItem(request)

'''Health and safety reports'''
#Get information about all reports e.g. the creation date, size, name
@api_view(['GET'])
def allReportsInfo(request):
    return ReportController.getAllReportInfo()

@api_view(['GET'])
def generateReport(request):
    return ReportController.getNewReport()

@api_view(['GET'])
def returnReport(request,filename):
    return ReportController.getReport(filename)

'''Front/Back door unlocking/locking'''
@api_view(['POST'])
def unlockDoor(request):
    # if delivery driver unlock back door
    if request.user.fridge_access:
        response = None
        if request.user.role == 'DD':
            print(f'unlocking back door')
            response = DoorController.unlockBackDoor()
            if response.status_code == 200:
                t = threading.Thread(target=DoorController.autoLockDoor,args=[DoorController.BACK_DOOR], daemon=True)
                t.start()
        else:
            print(f'unlocking front door')
            response = DoorController.unlockFrontDoor()
            if response.status_code == 200:
                t = threading.Thread(target=DoorController.autoLockDoor,args=[DoorController.FRONT_DOOR], daemon=True)
                t.start()
        return response
    response = {
        "error": "You do not have access to the fridge, please speak to head chef or system administrator"
    }
    return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def lockDoor(request):
    # if delivery driver lock back door else it must be a chef so use front door
    if request.user.fridge_access:
        if request.user.role == 'DD':
            return DoorController.lockBackDoor()
        else:
            return DoorController.lockFrontDoor()
    response = {
        "error": "You do not have access to the fridge, please speak to head chef or system administrator"
    }
    return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def doorLockStatus(request):
    return DoorController.returnAllDoorStatus(request)

'''Activity log'''
@api_view(['GET'])
def recentActivityLogs(request):
    return ActivityLogController.getLatestLogs()

@api_view(['GET'])
def returnLog(request, filename):
     return ActivityLogController.downloadLog(filename)

'''Notifications'''
@api_view(['GET'])
def allNotifications(request):
    if request.user.id == None or request.user.role != 'HC':
        response = {
            "error": "You do not have access to notifications, if this is wrong please contact system admin"
        }
        return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)
    return NotificationController.getAllNotifications(request)

@api_view(['DELETE'])
def deleteNotification(request, pk):
    if request.user.id == None or request.user.role != 'HC':
        response = {
            "error": "You are not authorised to delete notifications, if this is wrong please contact system admin"
        }
        return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)
    return NotificationController.deleteNotification(request, pk)

@api_view(['GET'])
def userOrders(request, pk):
    if request.user.id == None or request.user.role != 'DD':
        response = {
            "error": "You are not authorised to view deliveries, if this is wrong please contact system admin"
        }
        return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)
    return OrderController.getUserOrders(pk)

@api_view(['GET'])
def allOrders(request):
    return OrderController.getAllOrders()

@api_view(['PUT'])
def completeDelivery(request, pk):
    return OrderController.updateDelivered(pk)

@api_view(['POST'])
def createOrder(request):
    if request.user.id == None or request.user.role != 'HC':
        response = {
            "error": "You do not have permission to create orders, if this is wrong please contact system admin"
        }
        return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)
    return OrderController.createOrder(request)

@api_view(['POST'])
def createOrderItem(request):
    if request.user.id == None or request.user.role != 'HC':
        response = {
            "error": "You do not have permission to create order items, if this is wrong please contact system admin"
        }
        return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)
    return OrderItemController.createOrderItem(request)
    
@api_view(['GET'])
def allOrderItems(request):
    return OrderItemController.getOrderItems()
    
    