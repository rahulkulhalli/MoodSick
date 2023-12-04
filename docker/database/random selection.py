from pymongo import MongoClient
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['moodsick_db']

# Specify the collection name
collection = db['users']

# Count the number of documents in the collection
total_users = collection.count_documents({})

# Randomly select one user
random_user = collection.aggregate([
    { '$sample': { 'size': 1 } }
]).next()

# Print the randomly selected user
print(random_user)

# Specify the collection name
collection = db['spotify_data']

# Count the number of documents in the collection
total_songs = collection.count_documents({})

# Randomly select five songs
random_skip = random.randint(0, total_songs - 5)
random_songs = collection.find().skip(random_skip).limit(5)

# Print the randomly selected songs
for song in random_songs:
    print(song)


random_songs_list = [song for song in random_songs]
print(random_songs_list)


