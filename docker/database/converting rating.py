# from pymongo import MongoClient

# # Connect to MongoDB
# client = MongoClient('mongodb://localhost:27017')
# db = client['moodsick_db']  
# collection = db['songs']  

# # Update the data type of the field
# collection.update_many(
#     { 'global_rating': { '$exists': True, '$type': 16 } },  # $type 16 represents int in MongoDB
#     { '$set': { 'global_rating': { '$toDouble': '$global_rating' } } }
# )


from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['moodsick_db']
collection = db['songs']

# # Update the data type of the field and set an initial value if no rating is provided
# collection.update_many(
#     { 'global_rating': { '$exists': True, '$eq': None } },  # Check if the field exists and is null
#     { '$set': { 'global_rating': 0.0 } }
# )


# Update the data type of the field and set an initial value if no rating is provided
collection.update_many(
    {
        'global_rating': {
            '$exists': True,
            '$not': { '$type': 6 }  
        }
    },
    { '$set': { 'global_rating': 0.0 } })
