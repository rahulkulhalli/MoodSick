from app.models.spotify_communication import SpotifyPlaylist, SpotifyRecommendationInput, SongFeature
from . import db_name as collection
from bson.objectid import ObjectId
from typing import List


async def save_track_audio_preferances(user_id, spotify_communications: SongFeature):
    
    # print(spotify_communications)
    # save the data to db in the format:
    # {user_id: "user_id", songs_data: [{song_id: "song_id", danceability: 0.5, energy: 0.5, ...}, ...]}
    all_data = list()
    for feature_list in spotify_communications:
        if isinstance(feature_list, SongFeature):
            all_data.append(feature_list.dict())
        elif isinstance(feature_list, list) and isinstance(feature_list[0], SongFeature):
            for feature in feature_list:
                all_data.append(feature.dict())
        else:
            print(f"WTF???????????????? {feature_list}")
    # print(f"Save Track Audio Preferance: {all_data}")
    data = {
        "user_id": user_id,
        "songs_data": all_data,
    }
    
    _id = collection.track_features.insert_one(data)
    # user = users_serializer(collection.find({"_id": _id.inserted_id}))
    return {"status": "Ok","data": "user"}

async def get_track_audio_preferances(user_id):
    user = collection.track_features.find_one({"user_id": user_id})
    return user.get("songs_data")