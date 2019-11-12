from app import app, db, Movie, User
import unittest

class WatchListTestCase(unittest.TestCase):
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
