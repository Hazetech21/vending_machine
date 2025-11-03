
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import User, Product, ActiveSession
from .serializers import UserSerializer, LoginSerializer, ProductSerializer, DepositSerializer, BuySerializer
from .authentication import JWTAuthentication, generate_jwt_token
from .permissions import IsSeller, IsBuyer, IsSellerOwner
from .schemas import (
    register_schema, login_schema, logout_schema, logout_all_schema, force_logout_all_schema,
    product_list_schema, product_detail_schema, balance_schema, deposit_schema, buy_schema, reset_schema
)

@register_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if ActiveSession.objects.filter(user=user).exists():
        return Response({
            'error': 'There is already an active session using your account',
            'message': 'Use /logout/all to terminate all active sessions'
        }, status=status.HTTP_403_FORBIDDEN)
    
    token = generate_jwt_token(user)
    ActiveSession.objects.create(user=user, token=token)
    
    return Response({
        'token': token,
        'user': UserSerializer(user).data
    }, status=status.HTTP_200_OK)

@logout_schema
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    token = request.auth
    ActiveSession.objects.filter(token=token).delete()
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

@logout_all_schema
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_all(request):
    ActiveSession.objects.filter(user=request.user).delete()
    return Response({'message': 'All sessions terminated successfully'}, status=status.HTTP_200_OK)

@force_logout_all_schema
@api_view(['POST'])
@permission_classes([AllowAny])
def force_logout_all(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    ActiveSession.objects.filter(user=user).delete()
    return Response({'message': 'All sessions terminated successfully. You can now login.'}, status=status.HTTP_200_OK)

@product_list_schema
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.select_related('seller').all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        if request.user.role != 'seller':
            return Response({'error': 'Only sellers can create products'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@product_detail_schema
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('seller'), pk=pk)
    
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        if request.user.role != 'seller':
            return Response({'error': 'Only sellers can update products'}, status=status.HTTP_403_FORBIDDEN)
        
        if product.seller != request.user:
            return Response({'error': 'You can only update your own products'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if request.user.role != 'seller':
            return Response({'error': 'Only sellers can delete products'}, status=status.HTTP_403_FORBIDDEN)
        
        if product.seller != request.user:
            return Response({'error': 'You can only delete your own products'}, status=status.HTTP_403_FORBIDDEN)
        
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@balance_schema
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsBuyer])
def balance(request):
    return Response({
        'username': request.user.username,
        'deposit': request.user.deposit
    }, status=status.HTTP_200_OK)

@deposit_schema
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsBuyer])
def deposit(request):
    serializer = DepositSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    coin = serializer.validated_data['coin']
    user = request.user
    
    new_deposit = user.deposit + coin
    if new_deposit > 10000:
        return Response({'error': 'Maximum deposit limit is 10000 cents'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.deposit = new_deposit
    user.save()
    
    return Response({
        'message': f'{coin} cents deposited successfully',
        'current_deposit': user.deposit
    }, status=status.HTTP_200_OK)

@buy_schema
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsBuyer])
def buy(request):
    serializer = BuySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    product_id = serializer.validated_data['product_id']
    amount = serializer.validated_data['amount']
    
    try:
        with transaction.atomic():
            product = Product.objects.select_for_update().select_related('seller').get(id=product_id)
            user = User.objects.select_for_update().get(id=request.user.id)
            
            if product.amount_available < amount:
                return Response({'error': 'Insufficient product stock'}, status=status.HTTP_400_BAD_REQUEST)
            
            total_cost = product.cost * amount
            
            if user.deposit < total_cost:
                return Response({'error': 'You have insufficient fund for this purchase'}, status=status.HTTP_400_BAD_REQUEST)
            
            product.amount_available -= amount
            product.save()
            
            change = user.deposit - total_cost
            user.deposit = 0
            user.save()
            
            change_breakdown = calculate_change(change)
            
            return Response({
                'total_spent': total_cost,
                'product_purchased': product.product_name,
                'amount_purchased': amount,
                'change': change_breakdown
            }, status=status.HTTP_200_OK)
    
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

@reset_schema
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsBuyer])
def reset(request):
    user = request.user
    previous_deposit = user.deposit
    user.deposit = 0
    user.save()
    
    return Response({
        'message': 'Deposit reset successfully',
        'previous_deposit': previous_deposit,
        'current_deposit': 0
    }, status=status.HTTP_200_OK)


def calculate_change(amount):
    coins = [100, 50, 20, 10, 5]
    change_breakdown = []
    
    for coin in coins:
        while amount >= coin:
            change_breakdown.append(coin)
            amount -= coin
    
    return change_breakdown


#       product.amount_available -= amount
#             product.save()
            
#             change = user.deposit - total_cost
#             user.deposit = 0
#             user.save()        
#             return Response({
#                 'total_spent': total_cost,
#                 'product_purchased': product.product_name,
#                 'amount_purchased': amount,
#                 'change': change
#             }, status=status.HTTP_200_OK)