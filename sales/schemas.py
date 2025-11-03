from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import status


register_schema = extend_schema(
    summary="Register a new user",
    description="Create a new user account with either 'buyer' or 'seller' role.",
    request={
        'application/json': {
            'example': {
                'username': 'john_doe',
                'password': 'SecurePass123!',
                'role': 'buyer'
            }
        }
    },
    responses={
        201: {
            'description': 'User registered successfully',
            'example': {
                'message': 'User registered successfully',
                'user': {
                    'id': 1,
                    'username': 'john_doe',
                    'role': 'buyer',
                    'deposit': 0
                }
            }
        },
        400: {
            'description': 'Bad request - validation errors',
            'example': {
                'username': ['This field is required.'],
                'password': ['This password is too short.']
            }
        }
    },
    tags=['Authentication']
)


login_schema = extend_schema(
    summary="Login user",
    description="Authenticate user and receive JWT token. Only one active session per user is allowed.",
    request={
        'application/json': {
            'example': {
                'username': 'john_doe',
                'password': 'SecurePass123!'
            }
        }
    },
    responses={
        200: {
            'description': 'Login successful',
            'example': {
                'token': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                'user': {
                    'id': 1,
                    'username': 'john_doe',
                    'role': 'buyer',
                    'deposit': 0
                }
            }
        },
        401: {
            'description': 'Invalid credentials',
            'example': {'error': 'Invalid credentials'}
        },
        403: {
            'description': 'Active session exists',
            'example': {
                'error': 'There is already an active session using your account',
                'message': 'Use /logout/all to terminate all active sessions'
            }
        }
    },
    tags=['Authentication']
)


logout_schema = extend_schema(
    summary="Logout current session",
    description="Terminate the current active session.",
    responses={
        200: {
            'description': 'Logged out successfully',
            'example': {'message': 'Logged out successfully'}
        }
    },
    tags=['Authentication']
)


logout_all_schema = extend_schema(
    summary="Logout all sessions",
    description="Terminate all active sessions for the authenticated user.",
    responses={
        200: {
            'description': 'All sessions terminated',
            'example': {'message': 'All sessions terminated successfully'}
        }
    },
    tags=['Authentication']
)


force_logout_all_schema = extend_schema(
    summary="Force logout all sessions",
    description="Terminate all active sessions without requiring a token. Useful when you forgot to save your token.",
    request={
        'application/json': {
            'example': {
                'username': 'john_doe',
                'password': 'SecurePass123!'
            }
        }
    },
    responses={
        200: {
            'description': 'All sessions terminated',
            'example': {'message': 'All sessions terminated successfully. You can now login.'}
        },
        401: {
            'description': 'Invalid credentials',
            'example': {'error': 'Invalid credentials'}
        }
    },
    tags=['Authentication']
)


product_list_schema = extend_schema(
    summary="List all products or create new product",
    description="GET: Retrieve all products (any authenticated user). POST: Create new product (seller only).",
    request={
        'application/json': {
            'example': {
                'product_name': 'Coca Cola',
                'cost': 50,
                'amount_available': 20
            }
        }
    },
    responses={
        200: {
            'description': 'List of products',
            'example': [
                {
                    'id': 1,
                    'product_name': 'Coca Cola',
                    'amount_available': 20,
                    'cost': 50,
                    'seller_id': 1,
                    'seller_username': 'seller1',
                    'created_at': '2025-10-30T10:00:00Z',
                    'updated_at': '2025-10-30T10:00:00Z'
                }
            ]
        },
        201: {
            'description': 'Product created successfully',
            'example': {
                'id': 1,
                'product_name': 'Coca Cola',
                'amount_available': 20,
                'cost': 50,
                'seller_id': 1,
                'seller_username': 'seller1',
                'created_at': '2025-10-30T10:00:00Z',
                'updated_at': '2025-10-30T10:00:00Z'
            }
        },
        403: {
            'description': 'Only sellers can create products',
            'example': {'error': 'Only sellers can create products'}
        }
    },
    tags=['Products']
)


product_detail_schema = extend_schema(
    summary="Get, update or delete a product",
    description="GET: Any authenticated user. PUT/DELETE: Only the seller who created the product.",
    request={
        'application/json': {
            'example': {
                'product_name': 'Pepsi',
                'cost': 55,
                'amount_available': 15
            }
        }
    },
    responses={
        200: {
            'description': 'Product details or updated successfully',
            'example': {
                'id': 1,
                'product_name': 'Pepsi',
                'amount_available': 15,
                'cost': 55,
                'seller_id': 1,
                'seller_username': 'seller1',
                'created_at': '2025-10-30T10:00:00Z',
                'updated_at': '2025-10-30T10:30:00Z'
            }
        },
        204: {
            'description': 'Product deleted successfully',
            'example': {'message': 'Product deleted successfully'}
        },
        403: {
            'description': 'You can only modify your own products',
            'example': {'error': 'You can only update your own products'}
        },
        404: {
            'description': 'Product not found',
            'example': {'detail': 'Not found.'}
        }
    },
    tags=['Products']
)


balance_schema = extend_schema(
    summary="Get buyer balance",
    description="Retrieve the current deposit balance for the authenticated buyer.",
    responses={
        200: {
            'description': 'Current balance',
            'example': {
                'username': 'buyer1',
                'deposit': 150
            }
        },
        403: {
            'description': 'Only buyers can access this endpoint',
            'example': {'detail': 'You do not have permission to perform this action.'}
        }
    },
    tags=['Buyer Operations']
)


deposit_schema = extend_schema(
    summary="Deposit coins",
    description="Deposit a single coin into your account. Only accepts 5, 10, 20, 50, or 100 cent coins. Maximum deposit limit is 10,000 cents.",
    request={
        'application/json': {
            'example': {'coin': 100}
        }
    },
    responses={
        200: {
            'description': 'Coin deposited successfully',
            'example': {
                'message': '100 cents deposited successfully',
                'current_deposit': 250
            }
        },
        400: {
            'description': 'Invalid coin or deposit limit exceeded',
            'examples': {
                'invalid_coin': {
                    'summary': 'Invalid coin denomination',
                    'value': {'coin': ['Only [5, 10, 20, 50, 100] cent coins are accepted']}
                },
                'limit_exceeded': {
                    'summary': 'Deposit limit exceeded',
                    'value': {'error': 'Maximum deposit limit is 10000 cents'}
                }
            }
        },
        403: {
            'description': 'Only buyers can deposit',
            'example': {'detail': 'You do not have permission to perform this action.'}
        }
    },
    tags=['Buyer Operations']
)


buy_schema = extend_schema(
    summary="Buy product",
    description="Purchase a product using deposited coins. Returns total spent, product details, and change. Deposit is reset to 0 after purchase (change is returned).",
    request={
        'application/json': {
            'example': {
                'product_id': 1,
                'amount': 2
            }
        }
    },
    responses={
        200: {
            'description': 'Purchase successful',
            'example': {
                'total_spent': 100,
                'product_purchased': 'Coca Cola',
                'amount_purchased': 2,
                'change': [20, 20]
            }
        },
        400: {
            'description': 'Insufficient funds or stock',
            'examples': {
                'insufficient_funds': {
                    'summary': 'Insufficient balance',
                    'value': {'error': 'You have insufficient fund for this purchase'}
                },
                'insufficient_stock': {
                    'summary': 'Out of stock',
                    'value': {'error': 'Insufficient product stock'}
                }
            }
        },
        404: {
            'description': 'Product not found',
            'example': {'error': 'Product not found'}
        },
        403: {
            'description': 'Only buyers can purchase',
            'example': {'detail': 'You do not have permission to perform this action.'}
        }
    },
    tags=['Buyer Operations']
)


reset_schema = extend_schema(
    summary="Reset deposit",
    description="Reset your deposit balance back to 0. Useful when you want to get your money back without making a purchase.",
    responses={
        200: {
            'description': 'Deposit reset successfully',
            'example': {
                'message': 'Deposit reset successfully',
                'previous_deposit': 150,
                'current_deposit': 0
            }
        },
        403: {
            'description': 'Only buyers can reset deposit',
            'example': {'detail': 'You do not have permission to perform this action.'}
        }
    },
    tags=['Buyer Operations']
)