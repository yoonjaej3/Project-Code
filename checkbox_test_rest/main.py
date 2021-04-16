from flask import Flask, render_template, request
from database import menulist

app = Flask(__name__)
@app.route('/')

def index():
    content_list=menulist.get_menu()
    html = render_template('index.html', data_list=content_list)
    return html

@app.route('/insert', methods=['post'])
def insert() :
    #element = request.values.get('insert')
    element = request.form.getlist('menu')
    print(element)
    
    menulist.cart_insert(element)

    return '''
            <script>
                alert("저장되었습니다")
                location.href="."
            </script>
           ''' 

if __name__ == '__main__':
    app.run(port=5000,debug=True)


