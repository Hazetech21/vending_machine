from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class User(AbstractUser):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    deposit = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'users'
        
    def clean(self):
        if self.deposit > 10000:
            raise ValidationError({'deposit': 'Maximum deposit is 10000 cents'})
    
    def __str__(self):
        return self.username


class ActiveSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_sessions')
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'active_sessions'
        indexes = [
            models.Index(fields=['user', 'token']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    amount_available = models.IntegerField(validators=[MinValueValidator(0)])
    cost = models.IntegerField(validators=[MinValueValidator(5)])
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['seller']),
        ]
    
    def clean(self):
        if self.cost % 5 != 0:
            raise ValidationError({'cost': 'Cost must be in multiples of 5'})
    
    def __str__(self):
        return self.product_name