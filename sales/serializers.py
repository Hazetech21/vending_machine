from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Product


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role', 'deposit']
        read_only_fields = ['deposit']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProductSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'amount_available', 'cost', 'seller_id', 'seller_username', 'created_at', 'updated_at']
        read_only_fields = ['seller_id', 'seller_username', 'created_at', 'updated_at']
    
    def validate_cost(self, value):
        if value % 5 != 0:
            raise serializers.ValidationError("Cost must be in multiples of 5")
        return value
    
    def validate_amount_available(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount available cannot be negative")
        return value


class DepositSerializer(serializers.Serializer):
    coin = serializers.IntegerField()
    
    def validate_coin(self, value):
        valid_coins = [5, 10, 20, 50, 100]
        if value not in valid_coins:
            raise serializers.ValidationError(f"Only {valid_coins} cent coins are accepted")
        return value


class BuySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)