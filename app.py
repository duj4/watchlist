from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

# 数据库URI前缀校验
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///' # 如果是windows系统，使用三个斜线
else:
    prefix = 'sqlite:////' # 否则使用四个斜线

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控

#初始化扩展，传入程序实例app
db = SQLAlchemy(app)

# 创建数据库模型

# ORM中，类名即表名，自动生成并进行小写处理，表名即user
# 模型类声明要继承db.Model
class User(db.Model):
    # ORM中，类属性即列名
    id = db.Column(db.Integer,primary_key=True) # 主键
    name = db.Column(db.String(20)) # 名字
# 同上，表名即movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份

# 代码模拟数据
@app.cli.command()
def forge():
    """Generate fake data"""
    db.create_all()

    # 将原来的模拟数据移动到下面
    name = 'Jason Du'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    # 对创建的两个类（表名）进行实例化
    user = User(name=name)
    db.session.add(user)

    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done!')

# 模拟数据
# name = 'Jason Du'
# movies = [
#     {'title': 'My Neighbor Totoro', 'year': '1988'},
#     {'title': 'Dead Poets Society', 'year': '1989'},
#     {'title': 'A Perfect World', 'year': '1993'},
#     {'title': 'Leon', 'year': '1994'},
#     {'title': 'Mahjong', 'year': '1996'},
#     {'title': 'Swallowtail Butterfly', 'year': '1996'},
#     {'title': 'King of Comedy', 'year': '1999'},
#     {'title': 'Devils on the Doorstep', 'year': '1999'},
#     {'title': 'WALL-E', 'year': '2008'},
#     {'title': 'The Pork of Music', 'year': '2012'},
# ]

@app.route('/')
@app.route('/hello')
@app.route('/index')
@app.route('/home')
def index():
    # return "Welcome to my watchlist!"
    user = User.query.first() # 读取用户记录
    movies = Movie.query.all() # 读取所有电影记录
    return render_template('index.html',user=user, movies=movies)

@app.route('/totoro')
def totoro():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    return "Hello %s" % name

@app.route('/test')
def test_url_for():
    print(url_for('index'))
    print(url_for('user_page', name='duj4'))
    print(url_for('user_page', name='jason'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for',num=2))

    return "Test Page"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)