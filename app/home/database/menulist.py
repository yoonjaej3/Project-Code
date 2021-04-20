import pymysql

config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'mysql',
    'database': 'mydb'
}



def cart_insert(element):
    conn = pymysql.connect(**config)
    cur = conn.cursor()
    for i in element:
        sql = "insert into order_detail (order_id, menu_name, food_qty, food_price)\
               select 1, %s, 1, menu_price from menu where menu.menu_name=%s"
        cur.execute(sql, (i, i))
        
    conn.commit()
    conn.close()