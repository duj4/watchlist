from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/hello')
@app.route('/index')
@app.route('/home')
def hello():
    return "Welcome to my watchlist!"

@app.route('/totoro')
def totoro():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    return "Hello %s" % name

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='duj4'))
    print(url_for('user_page', name='jason'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for',num=2))

    return "Test Page"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)