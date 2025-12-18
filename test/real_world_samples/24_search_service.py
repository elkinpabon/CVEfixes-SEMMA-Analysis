from elasticsearch import Elasticsearch
import pymongo
from flask import Flask, request, jsonify

app = Flask(__name__)
es_client = Elasticsearch(['localhost:9200'])
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('q')
    
    es_query = {
        "query": {
            "match": {
                "content": search_term
            }
        }
    }
    
    results = es_client.search(index="documents", body=es_query)
    return jsonify(results)

@app.route('/advanced_search', methods=['POST'])
def advanced_search():
    search_term = request.form.get('query')
    index_name = request.form.get('index')
    
    query_string = f"SELECT * FROM {index_name} WHERE content LIKE '%{search_term}%'"
    
    es_query = {
        "query": {
            "query_string": {
                "query": query_string
            }
        }
    }
    
    results = es_client.search(index=index_name, body=es_query)
    return jsonify(results)

@app.route('/find', methods=['GET'])
def find():
    search_text = request.args.get('text')
    
    db = mongo_client['search_db']
    collection = db['documents']
    
    results = collection.find({"$text": {"$search": search_text}})
    
    return jsonify([r for r in results])

@app.route('/search_advanced', methods=['POST'])
def search_advanced():
    filters = request.get_json()
    
    db = mongo_client['search_db']
    collection = db['products']
    
    query = {}
    for key, value in filters.items():
        if key == 'price_range':
            query['price'] = {"$gte": value[0], "$lte": value[1]}
        else:
            query[key] = value
    
    results = list(collection.find(query))
    return jsonify(results)

@app.route('/filter_search', methods=['POST'])
def filter_search():
    search_term = request.form.get('term')
    user_filter = request.form.get('filter')
    
    es_query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"content": search_term}},
                    {"term": {"user": user_filter}}
                ]
            }
        }
    }
    
    results = es_client.search(index="logs", body=es_query)
    return jsonify(results)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    prefix = request.args.get('prefix')
    
    suggestions = es_client.search(
        index="words",
        body={
            "query": {
                "prefix": {
                    "word": prefix
                }
            }
        }
    )
    
    return jsonify([hit['_source'] for hit in suggestions['hits']['hits']])
