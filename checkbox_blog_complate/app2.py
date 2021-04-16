
from flask import Flask, render_template, jsonify, request
#pip install flask-mysqldb
import pymysql
app = Flask(__name__)
     
config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'mysql',
    'database': 'mydb1'
}

@app.route('/')
def main():
    return render_template('index.html')

@app.route("/insert",methods=["POST","GET"])
def insert():  
    conn = pymysql.connect(**config)
    insert = request.form['checkboxvalue'] 
    sql = '''
        INSERT INTO checkbox (name) VALUES (%s)
    '''
    cursor = conn.cursor()
    cursor.execute(sql, ([insert]))
    if request.method == 'POST':
        msg = 'Data Inserted Successfully!'
    else:
        msg = 'Invalid'

    conn.commit()
    conn.close()
    return jsonify(msg)
	
if __name__ == '__main__':
    app.run(debug=True)