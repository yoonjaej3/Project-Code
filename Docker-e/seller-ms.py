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


@app.route('/seller-ms')
def index():
    return "welcome to order microservice!"

class Seller(flask_restful.Resource):
    def __init__(self):
        self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()

    def get(self):
        db = pymysql.connect(**config)

        cur = db.cursor()
        sql = '''SELECT A.menu_name, B.total_price ,B.total_qty \
        from menu A INNER JOIN orders B ON A.store_id=B.store_id'''

        cur.execute(sql)
        data_list_two = ()
        data_list_two += cur.fetchall()  #1~4
        price = {}
        qty = {}
        menu_list = []
        for i in data_list_two:
            if (price.get(i[0]) == None):
                price[i[0]] = i[1]
                menu_list.append(i[0])
            else:
                price[i[0]] += i[1]

        for i in data_list_two:
            if (qty.get(i[0]) == None):
                qty[i[0]] = i[2]
            else:
                qty[i[0]] += i[2]

        data_list = []

        for i in menu_list:
            data_list.append([i, price[i], qty[i]])
        
        
        return jsonify(data_list)


api.add_resource(Seller, '/seller/seller-ms')
if __name__ == '__main__':
    app.run(port=6000)
