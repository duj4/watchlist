import unittest
from sayHello import sayHello

class SayHelloTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sayHello(self):  # 第 1 个测试
        rv = sayHello()
        self.assertEqual(rv, 'Hello!')

    def test_sayHello_to_somebody(self) : # 第 2 个测试
        rv = sayHello(to='Grey')
        self.assertEqual(rv, 'Hello, Grey!')

if __name__ == '__main__':
    unittest.main()