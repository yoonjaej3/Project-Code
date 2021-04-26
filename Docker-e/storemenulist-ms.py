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

@app.route('/storemenulist-ms')
def index():
    return "welcome to order microservice!"

class Storemenulist(flask_restful.Resource):
    def __init__(self):
        self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()

    def get(self, id):
        db = pymysql.connect(**config)

        cur = db.cursor()
        sql = '''select menu_id, menu_name, menu_price from menu where store_id=%s'''

        cur.execute(sql, id)
        data_list = cur.fetchall()

        a = list(data_list)
        a.insert(len(a), id)
        a = tuple(a)

        return jsonify(a)


api.add_resource(Storemenulist, '/storemenulist/storemenulist-ms/<int:id>')
if __name__ == '__main__':
    app.run(port=6000)