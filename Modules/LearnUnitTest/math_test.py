import unittest
from math_func import *


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("test Setup Class")

    @classmethod
    def tearDownClass(cls):
        print("test tear down Class")

    def setUp(self):
        method = self._testMethodName
        print("test Setup for {}".format(method))

    def tearDown(self):
        print("test tear down")

    def test_add(self):
        print("test_add")
        self.assertEqual(3, add(1, 2))
        self.assertNotEqual(3, add(1, 3))
        with self.assertRaises(TypeError):
            add('a', 2)

    def test_add2(self):
        print("test_add2")
        self.assertEqual(3, add(1, 2))
        self.assertNotEqual(3, add(1, 3))
        with self.assertRaises(TypeError):
            add('a', 2)


if __name__ == '__main__':
    unittest.main()
