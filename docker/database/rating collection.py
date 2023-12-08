from pymongo import MongoClient
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['moodsick_db']

# Specify the collections
user_collection = db['users']
song_collection = db['songs']
rating_collection = db['UserRatings']

# Function to get random user
def get_random_user():
    random_user = user_collection.aggregate([
        { '$sample': { 'size': 1 } }
    ]).next()
    return random_user

# Function to get random songs
def get_random_songs(n):
    total_songs = song_collection.count_documents({})
    random_skip = random.randint(0, total_songs - n)
    random_songs = song_collection.find().skip(random_skip).limit(n)
    return list(random_songs)

# Function to randomly rate songs for a user
def randomly_rate_songs(user, songs):
    credentials = user.get('credentials', {})
    username = credentials.get('username', 'Unknown')
    print(f"\nUser: {username}")
    print("Rating the following songs:")

    ratings = {}
    for song in songs:
        track_name = song.get('track_name', 'Unknown')
        artists = song.get('artists', [])
        artist_name = artists[0]['name'] if artists and isinstance(artists, list) else 'Unknown'
        random_rating = random.randint(0, 5)
        print(f"\nSong: {track_name} by {artist_name}")
        print(f"Rating: {random_rating}")
        ratings[str(song['_id'])] = random_rating

    return ratings

for i in range(150):

# Get a random user
    random_user = get_random_user()

# Get random songs
    random_songs = get_random_songs(6)

# Randomly rate songs for the user
    ratings = randomly_rate_songs(random_user, random_songs)

# Save ratings to the collection
    rating_collection.insert_one({
        'user_id': random_user['_id'],
        'ratings': ratings
    })

print("Ratings saved successfully.")
