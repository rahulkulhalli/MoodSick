from pymongo import MongoClient
from faker import Faker
from datetime import datetime
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['UserRecommendations']

fake = Faker()

# Function to get user recommendation history
def get_user_recommendation_history(user_id):
    return db.user_recommendations.find_one({'user_id': user_id})

# Function to update user recommendation history
def update_user_recommendation_history(user_id, recommended_songs):
    recommendation_doc = {
        'user_id': user_id,
        'recommended_songs': recommended_songs,
        'timestamp': datetime.now()
    }
    db.user_recommendations.insert_one(recommendation_doc)

# Generate recommendations for 150 users
for _ in range(150):
    # Assuming you have a 'users' collection with user documents
    user_document = db.users.aggregate([{ "$sample": { "size": 1 } }]).next()

    user_id = user_document['_id']
    user_history = get_user_recommendation_history(user_id)

    # Generate new recommendations excluding songs in user's history
    all_songs = db.songs.find()
    all_song_ids = [song['_id'] for song in all_songs]

    if user_history:
        # Exclude songs in user's recommendation history
        recommended_songs = list(set(all_song_ids) - set(user_history['recommended_songs']))
    else:
        # No history, recommend any 5 songs
        recommended_songs = random.sample(all_song_ids, 5)

    # Update the user's recommendation history
    update_user_recommendation_history(user_id, recommended_songs)

print("Recommendations generated for 150 users.")
