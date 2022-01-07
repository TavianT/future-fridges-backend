import re
import threading
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from rest_framework.decorators import api_view

from api.logging import ActivityLog
from .controllers import ActivityLogController, DoorController, ReportController, UserController, FridgeContentController, ItemController
from .serializers import UserSerializer

'''Auth function'''
#Used to login to the app via the backend, user information is saved as an instace and can be accessed without needing to pass any information about the current user
@csrf_exempt
def userLogin(request):
    #Takes data from form via POST request
    email = request.POST['email']
    password = request.POST['password']
    user = authenticate(request, username=email, password=password)
    if user is not None: #if login successful
        login(request, user)
        serializer = UserSerializer(user, many=False)
        return JsonResponse(serializer.data)
    else:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED) #return 401
    return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Logs the user out and clears instance
@csrf_exempt
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

'''Fridge Content functions'''

@api_view(['GET'])
#return all contents of the fridge
def allFridgeContent(request):
    return FridgeContentController.getAllFridgeContent()

'''@api_view(['POST'])
def singleFridgeContent(request,pk):
   # error = FridgeContentController.singleFridgeContentCreateCheck(pk) #
    #if error is None:  #commenting out for now
    if request.method == 'POST':
        return FridgeContentController.createFridgeContent(request)'''

@api_view(['POST'])
def createFridgeContent(request):
    return FridgeContentController.createFridgeContent(request)

@api_view(['PUT'])
def updateContentQuantity(request,pk):
    error = FridgeContentController.singleFridgeContentCreateCheck(pk)
    if error is None:
        return FridgeContentController.updateQuantity(request,pk)
    return error
            

'''Item functions'''
@api_view(['GET'])
def allItems(request):
    return ItemController.getAllItems()
#Get contents of item model from a barcode
@api_view(['GET'])
def singleItemFromBarcode(request):
    barcode = request.data['barcode']
    return ItemController.getItemFromBarcode(barcode)

'''@api_view(['GET','POST'])
def singleItem(request,pk):
    if request.method == 'POST':
        #create new item
        return ItemController.createItem(request) '''

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
    return HttpResponse(status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def lockDoor(request):
    # if delivery driver lock back door else it must be a chef so use front door
    if request.user.fridge_access:
        if request.user.role == 'DD':
            return DoorController.lockBackDoor()
        else:
            return DoorController.lockFrontDoor()
    return HttpResponse(status=status.HTTP_403_FORBIDDEN)


'''Activity log'''
api_view(['GET'])
def recentActivityLogs(request):
    return ActivityLogController.getLatestLogs()

api_view(['GET'])
def returnLog(request, filename):
     return ActivityLogController.downloadLog(filename)