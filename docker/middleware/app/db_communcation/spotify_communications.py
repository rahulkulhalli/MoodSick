from app.models.spotify_communications import SpotifyPlaylist, ModelParams, SongFeature
from . import db_name as collection


async def save_track_audio_preferances():
    # _id = collection.track_features.insert_one(dict(spotify_communications))
    # user = users_serializer(collection.find({"_id": _id.inserted_id}))
    return {"status": "Ok","data": "user"}
