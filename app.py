from flask import Flask, url_for, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# 扩展flask_login提供给了实现用户认证需要的各类功能函数
# login_required用于视图保护
# 在视图保护层面来说，未登录用户不能执行下面的操作：
# 访问编辑页面
# 访问设置页面
# 执行注销操作
# 执行删除操作
# 执行添加新条目操作
# 对于不允许未登录用户访问的视图，只需要为视图函数附加一个 login_required 装饰器就可以将未登录用户拒之门外

# flask-login是扩展库，需要单独安装
# Flask-Login 提供了一个 current_user 变量，注册这个函数的目的是，当程序运行后，如果用户已登录， current_user 变量的值会是当前用户的用户模型类记录
# 继承UserMixin这个类会让 User 类拥有几个用于判断认证状态的属性和方法，其中最常用的是 is_authenticated 属性：如果当前用户已经登录，那么 current_user.is_authenticated 会返回 True， 否则返回 False
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
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

# 初始化扩展，传入程序实例app
db = SQLAlchemy(app)

# 实例化扩展类
login_manager = LoginManager(app)
# 添加了@login_required装饰器后，如果未登录的用户访问对应的 URL，Flask-Login 会把用户重定向到登录页面，并显示一个错误提示
# 为了让这个重定向操作正确执行，我们还需要把 login_manager.login_view 的值设为我们程序的登录视图端点
login_manager.login_view = 'login'

@login_manager.user_loader
# 创建用户加载回调函数，接受user_id作为参数
def load_user(user_id):
    # 用ID作为User模型的主键查询对应的用户
    user = User.query.get(int(user_id))
    return user

# 创建数据库模型
# ORM中，类名即表名，自动生成并进行小写处理，表名即user
# 模型类声明要继承db.Model
class User(db.Model, UserMixin):
    # ORM中，类属性即列名
    id = db.Column(db.Integer,primary_key=True) # 主键
    name = db.Column(db.String(20)) # 名字
    username = db.Column(db.String(20)) #用户名
    password_hash = db.Column(db.String(128)) #密码散列值

    # 用来设置密码的方法，接受密码作为参数
    def set_password(self, password):
        # 将生成的密码保持到对应字段
        self.password_hash = generate_password_hash(password)
    # 用来验证密码的方法，接受密码作为参数
    def validate_password(self, password):
        # 返回布尔值
        return check_password_hash(self.password_hash, password)

# 同上，表名即movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 主键
    title = db.Column(db.String(60)) # 电影标题
    year = db.Column(db.String(4)) # 电影年份

# 生成管理员账户
@app.cli.command()
@click.option('--username', prompt=True, help='The username to login')
# hide_input会隐藏输入
# confirmation_prompt=True会要求二次确认密码输入
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password to login')
def admin(username, password):
    """create admin user"""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo("Updating user...")
        user.username = username
        user.set_password(password) # 设置密码
    else:
        click.echo("Creating user...")
        user = User(username=username, name="Admin")
        user.set_password(password) # 设置密码
        db.session.add(user)

    db.session.commit()
    click.echo("Done.")

# 删除并初始化DB
@app.cli.command()
@click.option('--drop', is_flag=True, help='drop database')
def initdb(drop):
    """initialize the database"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized database.")

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
    click.echo('Done.')

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
    return dict(user=user) # 需要返回字典，等同于return {'user':user},后续视图函数中的user关键字可以删除

# 默认只接受 GET 请求
# 两种方法的请求有不同的处理逻辑：对于 GET 请求，返回渲染后的页面；对于 POST 请求，则获取提交的表单数据并保存
@app.route('/', methods=['GET', 'POST'])
@app.route('/hello', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    # 添加新条目
    # 判断是否是POST请求
    if request.method == 'POST':
        # 如果当前用户未认证
        # 添加新条目的视图不能使用@login_required，因为当前视图同时还处理GET请求
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        else:
            # 获取表单数据
            # 传入表单对应输入字段Name的值
            title = request.form.get('title')
            year = request.form.get('year')
            # 验证数据
            if not title or not year or len(year) > 4 or len(title) >60:
                flash("Invalid input.") # 显示错误提示
                return redirect(url_for('index'))
            # 保存表单数据到数据库
            movie = Movie(title=title, year=year) # 创建记录
            db.session.add(movie) # 添加到数据库会话
            db.session.commit() # 提交数据库会话
            flash("Item created.") # 显示成功创建提示
            return redirect(url_for('index')) # 重定向回主页
    # return "Welcome to my watchlist!"
    # user = User.query.first() # 读取用户记录
    movies = Movie.query.all() # 读取所有电影记录
    # return render_template('index.html',user=user, movies=movies)
    return render_template('index.html', movies=movies)

# 编辑条目
# <int:movie_id> 部分表示 URL 变量，而 int 则是将变量转换成整型的 URL 变量转换器
@app.route('/movie/edit/<int:movie_id>', methods=['GET','POST'])
@login_required
def edit(movie_id):
    # get_or_404会返回对应主键的记录，如果没有找到，则返回 404 错误响应
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST': # 处理编辑表单的提交请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("Invalid input.")
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面
        movie.title = title # 更新标题
        movie.year = year # 更新年份
        db.session.commit() # 提交数据库会话
        flash("Item updated.")
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie) # 传入被编辑的电影记录

# 删除条目
@app.route('/movie/delete/<int:movie_id>', methods=['POST']) # 限定只接受POST请求
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id) # 获取电影记录
    db.session.delete(movie) # 删除对应记录
    db.session.commit() # 提交数据库会话
    flash("Item deleted.")
    return redirect(url_for('index')) # 重定向回主页

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("Invalid input.")
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user) # 登入用户
            flash("Login success.")
            return redirect(url_for('index'))
        # 如果验证失败
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    return render_template('login.html')

# 用户登出
@app.route('/logout')
@login_required # 用于视图保护
def logout():
    logout_user()
    flash("Goodbye.")
    return redirect(url_for('index'))

# 编辑
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # 支持修改用户名
        name = request.form['name']

        if not name or len(name) > 20:
            flash("Invalid input.")
            return redirect(url_for('settings'))

        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        current_user.name = name
        db.session.commit()
        flash("Settings updated.")
        return redirect(url_for('index'))

    return render_template('settings.html')


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