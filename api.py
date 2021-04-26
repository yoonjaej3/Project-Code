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
    'host': '172.20.0.1',
    'port': 13306,
    'user': 'root',
    'database': 'mydb'
}

# 카테고리 확인하기
@app.route('/category-ms')
def index_1():
    return "Get Category Data!"

@app.route('/festival-ms')
def index_2():
    return "Get Festival Data!"

@app.route('/festival2-ms')
def index_3():
    return "Show Earnings!"

@app.route('/seller-ms')
def index_4():
    return "Get seller's Information!"

@app.route('/storelist-ms')
def index_5():
    return "Get Store list!"

@app.route('/storemenulist-ms')
def index_6():
    return "What do they sell?"




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


# 페스티벌 조회하기
class Festival(flask_restful.Resource):
    def __init__(self):
        self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()
    
    def get(self):
        sql ="SELECT * from festival"
        self.cursor.execute(sql)
        data_list = self.cursor.fetchall()

        row_headers = [x[0] for x in self.cursor.description]
        

        json_data = []
        for result in data_list:
            json_data.append(dict(zip(row_headers, result)))

        return jsonify(json_data)


# 페스티벌 실적 조회
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


# 판매자 정보 조회
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


# 가게 리스트 조회
class Storelist(flask_restful.Resource):
    def __init__(self):
        self.conn = pymysql.connect(**config)
        self.cursor = self.conn.cursor()
    
    def get(self, f_id):
        sql ="select store_name, store_id, store_description, location_number \
             from store where festival_id=%s"
        self.cursor.execute(sql, [f_id])
        data_list = self.cursor.fetchall()

        row_headers = [x[0] for x in self.cursor.description]
        

        json_data = []
        for result in data_list:
            json_data.append(dict(zip(row_headers, result)))

        return jsonify(json_data)


# 가게별 판매목록 조회
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

api.add_resource(Storemenulist, '/storemenulist-ms/storemenulist/<int:id>')
api.add_resource(Storelist, '/storelist-ms/storelist/<int:f_id>')
api.add_resource(Seller, '/seller-ms/seller')
api.add_resource(Festival2, '/festival2-ms/festival2')
api.add_resource(Festival, '/festival-ms/festival')
api.add_resource(Category, '/category-ms/category')

if __name__ == '__main__':
    app.run(port=6000)