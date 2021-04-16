import pymysql

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
        sql = '''INSERT INTO orders (user_id, store_id, menu_name, total_qty, total_price) VALUE (%s, %s, %s, %s, %s)'''
        # price도 이름 조인해서 가지고 와야함..
        #price = '''select menu_price from menu where i = menu_name'''
        
        cur.execute(sql, (1, 3, i, 1, 24244))
   
  
    conn.commit()
    conn.close()