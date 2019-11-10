from flask import Flask, url_for, render_template, request, flash, redirect
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
# flash() 函数在内部会把消息存储到 Flask 提供的 session 对象里。
# session 用来在请求间存储数据，它会把数据签名后存储到浏览器的 Cookie 中，所以我们需要设置签名所需的密钥
app.config['SECRET_KEY'] = 'dev'

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

# 模板上下文处理函数
# 这个函数返回的变量（以字典键值对的形式）将会统一注入到每一个模板的上下文环境中，因此可以直接在模板中使用。
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user) # 需要返回字典，等同于return {'user':user},后续user关键字可以删除

# 默认只接受 GET 请求
# 两种方法的请求有不同的处理逻辑：对于 GET 请求，返回渲染后的页面；对于 POST 请求，则获取提交的表单数据并保存
@app.route('/', methods=['GET', 'POST'])
@app.route('/hello', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    # 判断是否是POST请求
    if request.method == 'POST':
        # 获取表单数据
        # 传入表单对应输入字段Name的值
        title = request.form.get('title')
        year = request.form.get('year')
        # 验证数据
        if not title or not year or len(year) > 4 or len(title) >60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index'))
        # 保存表单数据到数据库
        movie = Movie(title=title, year=year) # 创建记录
        db.session.add(movie) # 添加到数据库会话
        db.session.commit() # 提交数据库会话
        flash('Item created.') # 显示成功创建提示
        return redirect(url_for('index')) # 重定向回主页
    # return "Welcome to my watchlist!"
    # user = User.query.first() # 读取用户记录
    movies = Movie.query.all() # 读取所有电影记录
    # return render_template('index.html',user=user, movies=movies)
    return render_template('index.html', movies=movies)

# 编辑条目
@app.route('/movie/edit/<int:movie_id>', methods=['GET','POST'])
def edit(movie_id):
    # get_or_404会返回对应主键的记录，如果没有找到，则返回 404 错误响应
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST': # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面
        movie.title = title # 更新标题
        movie.year = year # 更新年份
        db.session.commit() # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie) # 传入被编辑的电影记录

# 删除条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST']) # 限定只接受POST请求
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) # 获取电影记录
    db.session.delete(movie) # 删除对应记录
    db.session.commit() # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index')) # 重定向回主页

# 错误处理函数，当404错误发生时，这个函数会被触发，返回值会作为响应主体返回给客户端
@app.errorhandler(404) #传入要处理的错误代码
def page_not_found(e): #接受异常对象作为参数
    user = User.query.first()
    # return render_template('404.html', user=user), 404 #返回模板和状态码，普通函数不需要写出状态码，因为默认是200
    return render_template('404.html'), 404

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