from flask import Flask, jsonify, request
from flask_restful import reqparse
from datetime import datetime

import flask_restful
import pymysql
import json
import uuid

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'mysql',
    'database': 'mydb1'
}

def get_menu():
    conn = pymysql.connect(**config)

    sql = '''
        select menu_name, menu_price
        from menu
        where store_id=3''' 

    cursor = conn.cursor()
    cursor.execute(sql)
    row = cursor.fetchall()

    data_list = []

    for obj in row :
        data_dic = {
            'menu_name' : obj[0],
            'menu_price' : obj[1]
        }
        data_list.append(data_dic)

    conn.close
    return data_list

def cart_insert(element):
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    for i in element:
        sql = "insert into order_detail (order_id, menu_name, food_qty, food_price)\
               select 1, %s, 1, menu_price from menu where menu.menu_name=%s"
        cur.execute(sql, (i, i))
        
    conn.commit()
    conn.close()