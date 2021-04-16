import flask
from flask import Flask, jsonify, request
from flask_restful import reqparse
from datetime import datetime

import flask_restful
# import mariadb
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
    'database': 'mydb1'
}

@app.route('/')
def index():
    return "Welcome to DELIVERY Microservice!"

class StoreList(flask_restful.Resource):
    def __init__(self):
        self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()
    
    def get(self):
        # 음식 카테고리 선택 후 해당 업체 리스트 뽑기
        # 치킨 / 피자 이런 카테고리 기준으로 조인
        # 처음 입력한 페스티벌도 조인해야 함
        # 전체 가게 알려면 select count(*) from store
        sql = '''select store_name, store_description, location_number
                 from store
                 where category="치킨"'''
        self.cursor.execute(sql)
        result_set = self.cursor.fetchall()

        row_headers = [x[0] for x in self.cursor.description]

        json_data = []
        for result in result_set:
            json_data.append(dict(zip(row_headers, result)))

        return jsonify(json_data)

api.add_resource(StoreList, '/storelist')

if __name__ == '__main__':
    app.run(port=6000)