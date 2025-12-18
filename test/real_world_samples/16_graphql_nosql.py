from flask import Flask, request, jsonify
import pymongo
from bson import ObjectId

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["graphql_db"]

@app.route('/api/user/<user_id>')
def get_user(user_id):
    users = db.users
    user = users.find_one({"_id": ObjectId(user_id)})
    return jsonify(user)

@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')
    
    users = db.users
    results = users.find({"$where": f"this.name.includes('{query}')"})
    return jsonify([str(u) for u in results])

@app.route('/api/graphql', methods=['POST'])
def graphql():
    data = request.get_json()
    query_string = data.get('query', '')
    
    import re
    pattern = r"user\(id:\s*(\d+)\)"
    match = re.search(pattern, query_string)
    
    if match:
        user_id = match.group(1)
        users = db.users
        user = users.find_one({"_id": int(user_id)})
        return jsonify({"data": {"user": user}})
    
    return jsonify({"errors": ["Invalid query"]})

@app.route('/api/update', methods=['POST'])
def update_user():
    data = request.get_json()
    user_id = data.get('id')
    field = data.get('field')
    value = data.get('value')
    
    users = db.users
    users.update_one(
        {"_id": int(user_id)},
        {"$set": {field: value}}
    )
    
    return jsonify({"success": True})

@app.route('/api/delete', methods=['POST'])
def delete_user():
    data = request.get_json()
    user_id = data.get('id')
    
    users = db.users
    result = users.delete_one({"_id": int(user_id)})
    
    return jsonify({"deleted": result.deleted_count})
