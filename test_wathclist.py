from app import app, db, Movie, User
import unittest

class WatchListTestCase(unittest.TestCase):
    # 测试flask程序
    def setUp(self):
        # 更新配置
        app.config.update(
            # 开启测试模式
            TESTTING = True,
            # 启用SQLite内存型数据库，不会干扰开发时使用的数据文件
            SQLALCEHMY_DATABASE_URI = 'sqlite:///:memory:'
        )

        # 创建数据库和表
        db.create_all()

        # 创建测试数据：一个用户和一个电影条目
        user = User(name = 'Test', username = 'test')
        user.set_password('123')
        movie = Movie(title = 'Test Movie Title', year = '2019')

        # 使用add_all()方法一次添加多个模型实例
        db.session.add_all([user, movie])
        db.session.commit()

        # 创建测试客户端, 用来模拟客户端请求
        self.client = app.test_client()
        # 创建测试命令运行器，用来触发自定义命令
        self.runner = app.test_cli_runner()

    def tearDown(selfs):
        # 清除数据库会话
        db.session.remove()
        # 删除数据库
        db.drop_all()

    # 测试程序实例是否存在
    def test_app_existence(self):
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_in_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试客户端
    # 调用这类方法返回包含响应数据的响应对象，对这个响应对象调用 get_data() 方法并把 as_text 参数设为 True 可以获取 Unicode 格式的响应主体
    # 测试404页面
    def test_404_page(self):
        # 上面的app.test_client()返回一个测试客户端对象，可以用来模拟客户端（浏览器）
        # 对其调用get()方法就相当于浏览器向服务器发送GET请求，调用post()方法则相当于浏览器发送POST请求
        response = self.client.get('/nothing') # 传入目标URL
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404) # 判断响应状态码

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

    # 测试辅助方法，用于登入用户
    # follow_redirects 参数设为 True 可以跟随重定向，最终返回的会是重定向后的响应
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    # 测试创建条目
    def test_create_item(self):
        self.login()

        # 测试创建条目操作
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('New Movie', data)

        # 测试创建条目操作，但电影标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

        # 测试创建条目操作，但电影年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

    # 测试更新条目
    def test_update_item(self):
        self.login()

        # 测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2019', data)

        # 测试更新条目操作
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('New Movie Edited', data)

        # 测试更新条目操作，但电影标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

        # 测试更新条目操作，但电影年份为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited Again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertNotIn('New Movie Edited Again', data)
        self.assertIn('Invalid input.', data)

    # 测试删除条目
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)