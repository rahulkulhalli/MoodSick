import json

# Load your existing JSON data from a file
with open('moodsick_db.songs.json', 'r') as file:
    data = json.load(file)

# Define the new column and its default value
new_column_name = "global_rating"
default_value = 0

# Updating an existing column name
old_column_name = "label"
new_column_name = "genre"

# Iterate through each record and add the new column
for record in data:
    record[new_column_name] = default_value
    if old_column_name in record:
        record[new_column_name] = record.pop(old_column_name)

# Save the modified data back to the file
with open('moodsick_db.songs.json', 'w') as file:
    json.dump(data, file, indent=2)

