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


@app.route('/festival2-ms')
def index():
    return "welcome to order microservice!"

class Festival2(flask_restful.Resource):
    def __init__(self):
        self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()

    def get(self):
        db = pymysql.connect(**config)
        cur = db.cursor()
        sql = "SELECT A.order_id,A.total_price,B.festival_id,B.festival_name from orders A INNER JOIN festival B ON A.user_no=B.user_no"
        cur.execute(sql)

        data_list = cur.fetchall()
        
        
        return jsonify(data_list)



api.add_resource(Festival2, '/festival2/festival2-ms')
if __name__ == '__main__':
    app.run(port=6000)
