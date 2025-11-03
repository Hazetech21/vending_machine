from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Product, ActiveSession
import json


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.logout_all_url = reverse('logout_all')
    
    def test_register_buyer(self):
        data = {
            'username': 'buyer1',
            'password': 'TestPass123!',
            'role': 'buyer'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().role, 'buyer')
    
    def test_register_seller(self):
        data = {
            'username': 'seller1',
            'password': 'TestPass123!',
            'role': 'seller'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get().role, 'seller')
    
    def test_register_duplicate_username(self):
        User.objects.create_user(username='buyer1', password='Pass123!', role='buyer')
        data = {
            'username': 'buyer1',
            'password': 'TestPass123!',
            'role': 'buyer'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_success(self):
        User.objects.create_user(username='buyer1', password='TestPass123!', role='buyer')
        data = {'username': 'buyer1', 'password': 'TestPass123!'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(ActiveSession.objects.count(), 1)
    
    def test_login_invalid_credentials(self):
        User.objects.create_user(username='buyer1', password='TestPass123!', role='buyer')
        data = {'username': 'buyer1', 'password': 'WrongPass'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_active_session_exists(self):
        user = User.objects.create_user(username='buyer1', password='TestPass123!', role='buyer')
        data = {'username': 'buyer1', 'password': 'TestPass123!'}
        
        response1 = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        response2 = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('already an active session', response2.data['error'])
    
    def test_logout(self):
        user = User.objects.create_user(username='buyer1', password='TestPass123!', role='buyer')
        data = {'username': 'buyer1', 'password': 'TestPass123!'}
        login_response = self.client.post(self.login_url, data, format='json')
        token = login_response.data['token']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ActiveSession.objects.count(), 0)
    
    def test_logout_all(self):
        user = User.objects.create_user(username='buyer1', password='TestPass123!', role='buyer')
        ActiveSession.objects.create(user=user, token='token1')
        ActiveSession.objects.create(user=user, token='token2')
        
        data = {'username': 'buyer1', 'password': 'TestPass123!'}
        ActiveSession.objects.all().delete()
        login_response = self.client.post(self.login_url, data, format='json')
        token = login_response.data['token']
        
        ActiveSession.objects.create(user=user, token='dummy_token')
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(self.logout_all_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ActiveSession.objects.filter(user=user).count(), 0)


class ProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(username='seller1', password='Pass123!', role='seller')
        self.buyer = User.objects.create_user(username='buyer1', password='Pass123!', role='buyer')
        
        self.seller_token = self._login_user('seller1', 'Pass123!')
        self.buyer_token = self._login_user('buyer1', 'Pass123!')
        
        self.products_url = reverse('product_list')
    
    def _login_user(self, username, password):
        ActiveSession.objects.filter(user__username=username).delete()
        response = self.client.post(reverse('login'), {'username': username, 'password': password}, format='json')
        return response.data['token']
    
    def test_get_products_list(self):
        Product.objects.create(product_name='Coke', cost=50, amount_available=10, seller=self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_product_as_seller(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.seller_token}')
        data = {
            'product_name': 'Pepsi',
            'cost': 45,
            'amount_available': 20
        }
        response = self.client.post(self.products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
    
    def test_create_product_as_buyer_fails(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        data = {
            'product_name': 'Pepsi',
            'cost': 45,
            'amount_available': 20
        }
        response = self.client.post(self.products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_product_invalid_cost(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.seller_token}')
        data = {
            'product_name': 'Pepsi',
            'cost': 43,
            'amount_available': 20
        }
        response = self.client.post(self.products_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_own_product(self):
        product = Product.objects.create(product_name='Coke', cost=50, amount_available=10, seller=self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.seller_token}')
        url = reverse('product_detail', args=[product.id])
        data = {'cost': 55}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.cost, 55)
    
    def test_update_other_seller_product_fails(self):
        other_seller = User.objects.create_user(username='seller2', password='Pass123!', role='seller')
        product = Product.objects.create(product_name='Coke', cost=50, amount_available=10, seller=other_seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.seller_token}')
        url = reverse('product_detail', args=[product.id])
        data = {'cost': 55}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_own_product(self):
        product = Product.objects.create(product_name='Coke', cost=50, amount_available=10, seller=self.seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.seller_token}')
        url = reverse('product_detail', args=[product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
    
    def test_delete_other_seller_product_fails(self):
        other_seller = User.objects.create_user(username='seller2', password='Pass123!', role='seller')
        product = Product.objects.create(product_name='Coke', cost=50, amount_available=10, seller=other_seller)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.seller_token}')
        url = reverse('product_detail', args=[product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BuyerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(username='seller1', password='Pass123!', role='seller')
        self.buyer = User.objects.create_user(username='buyer1', password='Pass123!', role='buyer')
        
        ActiveSession.objects.all().delete()
        login_response = self.client.post(reverse('login'), {'username': 'buyer1', 'password': 'Pass123!'}, format='json')
        self.buyer_token = login_response.data['token']
        
        self.deposit_url = reverse('deposit')
        self.buy_url = reverse('buy')
        self.reset_url = reverse('reset')
        
        self.product = Product.objects.create(
            product_name='Coke',
            cost=50,
            amount_available=10,
            seller=self.seller
        )
    
    def test_deposit_valid_coin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(self.deposit_url, {'coin': 50}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.deposit, 50)
    
    def test_deposit_invalid_coin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(self.deposit_url, {'coin': 15}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_deposit_exceeds_limit(self):
        self.buyer.deposit = 9950
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(self.deposit_url, {'coin': 100}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_buy_product_success(self):
        self.buyer.deposit = 150
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(self.buy_url, {'product_id': self.product.id, 'amount': 2}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_spent'], 100)
        self.assertEqual(response.data['change'], [50])
        self.product.refresh_from_db()
        self.assertEqual(self.product.amount_available, 8)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.deposit, 0)
    
    def test_buy_insufficient_funds(self):
        self.buyer.deposit = 30
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(self.buy_url, {'product_id': self.product.id, 'amount': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('insufficient fund', response.data['error'])
    
    def test_buy_insufficient_stock(self):
        self.buyer.deposit = 1000
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(self.buy_url, {'product_id': self.product.id, 'amount': 20}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient product stock', response.data['error'])
    
    def test_buy_nonexistent_product(self):
        self.buyer.deposit = 100
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(self.buy_url, {'product_id': 9999, 'amount': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_reset_deposit(self):
        self.buyer.deposit = 200
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(self.reset_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['previous_deposit'], 200)
        self.buyer.refresh_from_db()
        self.assertEqual(self.buyer.deposit, 0)
    
    def test_seller_cannot_deposit(self):
        ActiveSession.objects.all().delete()
        seller_login = self.client.post(reverse('login'), {'username': 'seller1', 'password': 'Pass123!'}, format='json')
        seller_token = seller_login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {seller_token}')
        response = self.client.post(self.deposit_url, {'coin': 50}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_seller_cannot_buy(self):
        ActiveSession.objects.all().delete()
        seller_login = self.client.post(reverse('login'), {'username': 'seller1', 'password': 'Pass123!'}, format='json')
        seller_token = seller_login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {seller_token}')
        response = self.client.post(self.buy_url, {'product_id': self.product.id, 'amount': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_seller_cannot_reset(self):
        ActiveSession.objects.all().delete()
        seller_login = self.client.post(reverse('login'), {'username': 'seller1', 'password': 'Pass123!'}, format='json')
        seller_token = seller_login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {seller_token}')
        response = self.client.post(self.reset_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ChangeCalculationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(username='seller1', password='Pass123!', role='seller')
        self.buyer = User.objects.create_user(username='buyer1', password='Pass123!', role='buyer')
        
        ActiveSession.objects.all().delete()
        login_response = self.client.post(reverse('login'), {'username': 'buyer1', 'password': 'Pass123!'}, format='json')
        self.buyer_token = login_response.data['token']
        
        self.product = Product.objects.create(
            product_name='Coke',
            cost=65,
            amount_available=10,
            seller=self.seller
        )
    
    def test_change_calculation_35_cents(self):
        self.buyer.deposit = 100
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(reverse('buy'), {'product_id': self.product.id, 'amount': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['change'], [20, 10, 5])
    
    def test_change_calculation_95_cents(self):
        self.product.cost = 5
        self.product.save()
        self.buyer.deposit = 100
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(reverse('buy'), {'product_id': self.product.id, 'amount': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['change'], [50, 20, 20, 5])
    
    def test_no_change_exact_amount(self):
        self.product.cost = 100
        self.product.save()
        self.buyer.deposit = 100
        self.buyer.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.buyer_token}')
        response = self.client.post(reverse('buy'), {'product_id': self.product.id, 'amount': 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['change'], [])