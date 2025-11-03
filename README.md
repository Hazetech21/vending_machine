# Vending Machine API

A Django REST Framework API that simulates a vending machine system with role-based access control, allowing sellers to manage products and buyers to deposit coins and make purchases.

## Features

- **JWT Authentication** with session management
- **Role-based Access Control** (Buyer/Seller)
- **Product Management** (CRUD operations for sellers)
- **Coin Deposit System** (5, 10, 20, 50, 100 cent coins)
- **Purchase System** with automatic change calculation
- **Session Management** (prevent concurrent logins)
- **PostgreSQL Database** with optimized queries

## Tech Stack

- Python 3.11
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL 15
- JWT Authentication
- Docker & Docker Compose

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

## Setup Instructions

### Option 1: Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd vending_machine
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL database**
```bash
createdb vending_machine_db
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

6. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

8. **Run tests**
```bash
python manage.py test
```

9. **Start development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

### Option 2: Docker Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd vending_machine
```

2. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

3. **Run migrations (in separate terminal)**
```bash
docker-compose exec web python manage.py migrate
```

4. **Run tests**
```bash
docker-compose exec web python manage.py test
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/register/` - Register new user (buyer/seller)
- `POST /api/login/` - Login and get JWT token
- `POST /api/logout/` - Logout current session
- `POST /api/logout/all/` - Logout all sessions (requires token)
- `POST /api/logout/force/` - Force logout all sessions (requires username/password)

### Products
- `GET /api/products/` - List all products (authenticated)
- `POST /api/products/` - Create product (seller only)
- `GET /api/products/<id>/` - Get product details
- `PUT /api/products/<id>/` - Update product (owner only)
- `DELETE /api/products/<id>/` - Delete product (owner only)

### Buyer Operations
- `GET /api/balance/` - Get current deposit balance (buyer only)
- `POST /api/deposit/` - Deposit coins (buyer only)
- `POST /api/buy/` - Purchase product (buyer only)
- `POST /api/reset/` - Reset deposit to 0 (buyer only)


## Business Rules

1. **Coins**: Only 5, 10, 20, 50, and 100 cent coins accepted
2. **Product Cost**: Must be in multiples of 5
3. **Maximum Deposit**: 10,000 cents per buyer
4. **Change**: Automatically calculated and returned after purchase
5. **Stock Management**: Product stock decreases after purchase
6. **Session Control**: One active session per user at a time
7. **Role Permissions**:
   - Sellers: Create, update, delete their own products
   - Buyers: Deposit coins, buy products, reset deposit
   - Everyone: View all products

## Testing

Run all tests:
```bash
python manage.py test
```

Run specific test class:
```bash
python manage.py test api.tests.ProductTests
```

Run with coverage:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Database Schema

### User Model
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password
- `role`: 'buyer' or 'seller'
- `deposit`: Current balance (cents)

### Product Model
- `id`: Primary key
- `product_name`: Product name
- `cost`: Price in cents (multiples of 5)
- `amount_available`: Stock quantity
- `seller`: Foreign key to User
- `created_at`: Timestamp
- `updated_at`: Timestamp

### ActiveSession Model
- `id`: Primary key
- `user`: Foreign key to User
- `token`: JWT token
- `created_at`: Timestamp

## Edge Cases Handled

- ✅ Cost validation (must be multiples of 5)
- ✅ Deposit limit (max 10,000 cents)
- ✅ Stock validation (insufficient stock)
- ✅ Balance validation (insufficient funds)
- ✅ Seller ownership (can only modify own products)
- ✅ Role-based restrictions
- ✅ Concurrent session prevention
- ✅ Transaction atomicity for purchases
- ✅ Invalid coin rejection
- ✅ Token expiration handling

## Performance Optimizations

- `select_related()` for product-seller queries
- `select_for_update()` for purchase transactions
- Database indexes on frequently queried fields
- Atomic transactions for critical operations

## Security Features

- JWT token-based authentication
- Password hashing with Django's built-in validators
- Role-based access control
- Session management and validation
- CSRF protection
- SQL injection prevention (Django ORM)

## Admin Panel

Access the admin panel at `http://localhost:8000/admin/`

Create superuser:
```bash
python manage.py createsuperuser
```

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.