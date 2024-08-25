import LiteJsonDb
  
# Initialize the database with encryption enabled
db =  LiteJsonDb.JsonDB(crypted=True)

# Add some initial data
# Set data without extra-data
db.set_data("posts")

# Set data with extra-data
db.set_data("users/1", {"name": "Aliou", "age": 20})
db.set_data("users/2", {"name": "Coder", "age": 25})

# Modify existing data
db.edit_data("users/1", {"name": "Alex"})

# Retrieve and print data
print(db.get_data("users/1"))
print(db.get_data("users/2"))

# Remove data
db.remove_data("users/2")

# Perform a basic search
results = db.search_data("Aliou")
print("Basic Search Results:", results)

# Perform a key-specific search
results = db.search_data("Aliou", key="users")
print("Key-specific Search Results:", results)

# Retrieve the full database
print(db.get_db(raw=True))

# Work with subcollections
db.set_subcollection("groups", "1", {"name": "Admins"})
db.edit_subcollection("groups", "1", {"description": "Admin group"})
print(db.get_subcollection("groups"))
db.remove_subcollection("groups", "1")