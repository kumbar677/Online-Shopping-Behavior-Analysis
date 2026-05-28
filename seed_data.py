import random
import mysql.connector
from faker import Faker
from config import Config

fake = Faker()

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE
        )
    except mysql.connector.Error as err:
        print(f"Connection Error: {err}")
        return None

def generate_users(n=1000):
    users = []
    genders = ['Male', 'Female', 'Other']
    countries = ['USA', 'UK', 'India', 'Canada', 'Australia', 'Germany', 'France']
    for _ in range(n):
        name = fake.name()
        city = fake.city()
        state = fake.state()
        country = random.choices(countries, weights=[30, 15, 20, 10, 10, 10, 5], k=1)[0]
        age = random.randint(18, 75)
        gender = random.choices(genders, weights=[48, 48, 4], k=1)[0]
        users.append((name, city, state, country, age, gender))
    return users

def generate_products(n=200):
    products = []
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Beauty', 'Sports', 'Toys']
    brands = ['Sony', 'Nike', 'Samsung', 'Adidas', 'LG', 'Apple', 'Puma', 'L\'Oreal']
    for _ in range(n):
        name = fake.word().capitalize() + " " + fake.word().capitalize()
        category = random.choice(categories)
        price = round(random.uniform(10.0, 1500.0), 2)
        brand = random.choice(brands)
        discount = round(random.uniform(0, 30.0), 2)
        products.append((name, category, price, brand, discount))
    return products

def generate_orders(n=5000, num_users=1000, num_products=200):
    orders = []
    payment_methods = ['Credit Card', 'PayPal', 'Debit Card', 'Apple Pay', 'Google Pay']
    
    for _ in range(n):
        user_id = random.randint(1, num_users)
        product_id = random.randint(1, num_products)
        quantity = random.randint(1, 5)
        date = fake.date_between(start_date='-2y', end_date='today')
        total_amount = round(random.uniform(15.0, 5000.0), 2)
        payment_method = random.choices(payment_methods, weights=[45, 25, 15, 10, 5], k=1)[0]
        orders.append((user_id, product_id, quantity, date, total_amount, payment_method))
    return orders

def seed_database():
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database.")
        return
    
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] > 0:
        print("Database already contains data. Skipping seeding.")
        conn.close()
        return

    print("Generating users...")
    users = generate_users(1000)
    cursor.executemany("INSERT INTO Users (name, city, state, country, age, gender) VALUES (%s, %s, %s, %s, %s, %s)", users)
    
    print("Generating products...")
    products = generate_products(200)
    cursor.executemany("INSERT INTO Products (name, category, price, brand, discount) VALUES (%s, %s, %s, %s, %s)", products)
    
    print("Generating orders...")
    orders = generate_orders(5000, 1000, 200)
    cursor.executemany("INSERT INTO Orders (user_id, product_id, quantity, date, total_amount, payment_method) VALUES (%s, %s, %s, %s, %s, %s)", orders)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Database seeded successfully with 1000 users, 200 products, and 5000 orders!")

if __name__ == '__main__':
    seed_database()
