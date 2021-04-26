import flask
from flask import Flask, jsonify, request
from flask_restful import reqparse
from datetime import datetime

import flask_restful
import pymysql
import json
import uuid

app = Flask(__name__)
api = flask_restful.Api(app)

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'mysql',
    'database': 'mydb'
}

@app.route('/category-ms')
def index():
    return "welcome to order microservice!"

class Category(flask_restful.Resource):
    def __init__(self):
        self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()
    
    def get(self):
        sql ="select category, count(category) as '가게 수' \
              from store group by category"
        self.cursor.execute(sql)
        # data_list = self.cursor.fetchone()
        data_list = self.cursor.fetchall()

        row_headers = [x[0] for x in self.cursor.description]
        

        json_data = []
        for result in data_list:
            json_data.append(dict(zip(row_headers, result)))

        return jsonify(json_data)


api.add_resource(Category, '/category-ms/category')
if __name__ == '__main__':
    app.run(port=6000)