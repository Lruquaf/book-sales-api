from pymongo import MongoClient

client = MongoClient("mongodb+srv://talha1:tt180475@clusteraymak.4twou.mongodb.net/?retryWrites=true&w=majority&appName=Clusteraymak")
db = client["book_sales2"]

# Test the connection
print(db.list_collection_names())
