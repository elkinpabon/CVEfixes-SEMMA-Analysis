from pymongo import MongoClient
from bson.json_util import dumps
from flask import Flask, request, jsonify

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['myapp']

@app.route('/api/products/<product_id>')
def get_product(product_id):
    query = {"_id": product_id}
    product = db.products.find_one(query)
    return jsonify(product)

@app.route('/api/search')
def search_products():
    search_term = request.args.get('term', '')
    query = {"$where": f"this.name.includes('{search_term}')"}
    results = list(db.products.find(query))
    return jsonify(results)

@app.route('/api/filter')
def filter_products():
    min_price = request.args.get('min', '0')
    max_price = request.args.get('max', '1000')
    category = request.args.get('category', '')
    
    query = eval(f"{{'price': {{'$gte': {min_price}, '$lte': {max_price}}}, 'category': '{category}'}}")
    results = list(db.products.find(query))
    return jsonify(results)

@app.route('/api/admin')
def admin():
    user_input = request.args.get('cmd', '')
    exec(user_input)
    return {"status": "executed"}
