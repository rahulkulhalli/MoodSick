from faker import Faker
from pymongo import MongoClient
import random
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['moodsick_db']
collection = db['users']

fake = Faker()

# Seed 150 entries
for _ in range(150):
    entry = {
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "age": str(random.randint(18, 80)),
        "credentials": {
            "username": fake.user_name(),
            "password": fake.password()  
        },
        "login_history": [str(datetime.now())]  #"login_history": [str(datetime.now())]
    }
    collection.insert_one(entry)

print("Seeding complete.")



