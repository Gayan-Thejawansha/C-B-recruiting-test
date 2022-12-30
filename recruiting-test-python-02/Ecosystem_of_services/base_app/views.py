from django.views.decorators.csrf import csrf_exempt
from base_app.serializers import InvestorSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from . import models
from django.db import IntegrityError
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny



@csrf_exempt
@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/investors',
        'GET /api/investors/:email',
        'POST /api/create-investor',
        'PUT /api/update-investor/:email',
        'GET /api/search-investors?QueryParams[name, email, phone]',
        'DELETE /api/delete-investor/:email',
        'POST /api/generate-auth',
    ]
    return Response(routes)

@csrf_exempt
@api_view(['GET'])
def getInvestors(request):
    investors = models.Investor.objects.all()
    serializer = InvestorSerializer(investors, many=True)
    return Response(serializer.data)

@csrf_exempt
@api_view(['GET'])
def getInvestor(request, em):
    investor = models.Investor.objects.get(email=em)
    serializer = InvestorSerializer(investor, many=False)
    return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
def createInvestor(request):
    # permission_classes = (IsAuthenticated,)
    try:
        _name = request.data['name']
        _email = request.data['email']
        _phone = request.data['phone']
        _description = request.data['description']
        investor = models.Investor(name = _name , email = _email, phone = _phone, description = _description)
    except Exception as e:
        return Response('Incorrect Or Incomplete set of parameters, Please check and retry', status=status.HTTP_400_BAD_REQUEST)
    try:
        investor.save()
        return Response('Successfully created the Investor.', status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        #error = 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)+ str(type(e).__name__) + str(e)
        error = str(e.__context__)
        if str(e.__context__) == 'UNIQUE constraint failed: base_app_investor.email':
            error = 'The email has been already registered. Please check and retry again' 
        return Response(error, status=status.HTTP_409_CONFLICT)
    except :
        error = 'Internal Server Error: Please contact the relevant team'
        return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['PUT'])
def updateInvestor(request):

    try:       
        _email = request.GET.get('email')
        investor = models.Investor.objects.get(email=_email)
        # print(investor)
    except Exception as e:
        return Response('Please provide a valid email of the Investor to be updated and retry', status=status.HTTP_400_BAD_REQUEST)
    try:
        try:
            investor.name = request.data['name']
        except:
            print ('No Name Update')
        try:
            investor.phone = request.data['phone']
        except:
            print ('No Phone Update')
        try:
            investor.description = request.data['description']
        except Exception as e:
            print(e)
            print ('No Description Update')
        
        # investor = models.Investor(name = _name , email = _email, phone = _phone, description = _description)
        investor.save()
        return Response('Successfully updated the Investor.', status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        #error = 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)+ str(type(e).__name__) + str(e)
        error = str(e.__context__)
        if str(e.__context__) == 'UNIQUE constraint failed: base_app_investor.email':
            error = 'The email has been already registered. Please check and retry again' 
        return Response(error, status=status.HTTP_409_CONFLICT)
    except :
        error = 'Internal Server Error: Please contact the relevant team'
        return Response(error, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt    
@api_view(['GET'])
def searchInvestors(request):
    _name = request.GET.get('name') if request.GET.get('name') != None else ''
    _email = request.GET.get('email') if request.GET.get('email') != None else ''
    _phone = request.GET.get('phone') if request.GET.get('phone') != None else ''
    investor = models.Investor.objects.filter(name__icontains=_name, email__icontains = _email, phone__icontains = _phone)
    serializer = InvestorSerializer(investor, many=True)
    return Response(serializer.data)

@csrf_exempt
@api_view(['DELETE'])
def deleteInvestor(request, em):

    try:
        investor = models.Investor.objects.get(email=em)
    except Exception as e:
        print (e)
        return Response('The requested Investor does not exist.', status=status.HTTP_404_NOT_FOUND)
    try :
        investor.delete()
    except Exception as e:
        print (e)
        return Response('Something wrong, I can feel it.', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # serializer = InvestorSerializer(investor, many=False)
    return Response('Successfully deleted the Investor.', status=status.HTTP_202_ACCEPTED)

@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def getAuthToken(request):
    try:
        userName = request.data['username']
        password = request.data['password']
    except Exception as e:
        print (e)
        return Response('Request is not complete, Please check and retry.', status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(username=userName)
    except Exception as e:
        return Response('Requested user does not exist.', status=status.HTTP_404_NOT_FOUND)
    userAuth = authenticate(request, username=userName, password=password)
    if userAuth is not None:
        token = Token.objects.get_or_create(user=user)
        print (token)
        print(token[0])
        results = {'Description' : 'Token generated successfully', 'Token':str(token[0]), 'New_Token' : token[1]}
        return Response(results, status=status.HTTP_202_ACCEPTED)
    else: 
        return Response('Authorization unsuccessful: Username OR password does not exit.', status=status.HTTP_401_UNAUTHORIZED)
