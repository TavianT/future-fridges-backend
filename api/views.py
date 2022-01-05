from django.http.response import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from rest_framework.decorators import api_view
from .reports import HealthAndSafetyReport
from .controllers import ReportController, UserController, FridgeContentController, ItemController

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
        return HttpResponse(status=status.HTTP_200_OK) #return 200 TODO: might need to change status code
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

@api_view(['POST'])
def singleFridgeContent(request,pk):
   # error = FridgeContentController.singleFridgeContentCreateCheck(pk) #
    #if error is None:  #commenting out for now
    if request.method == 'POST':
        return FridgeContentController.createFridgeContent(request)

@api_view(['PUT'])
def updateContentQuantity(request,pk):
    error = FridgeContentController.singleFridgeContentCreateCheck(pk)
    if error is None:
        response = FridgeContentController.updateQuantity(request,pk)
        if response.status_code > 299: #check if error code is 300 redirect, 400 user error or 500 server error
            return response
        #TODO: implement activity log
        return response
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

@api_view(['GET','POST'])
def singleItem(request,pk):
    if request.method == 'POST':
        #create new item
        return ItemController.createItem(request)

'''Health and safety reports'''
#Get information about all reports e.g. the creation date, size, name
@api_view(['GET'])
def allReportsInfo(request):
    return ReportController.getAllReportInfo()

@api_view(['GET'])
def generateReport(request):
    return ReportController.getNewReport()
