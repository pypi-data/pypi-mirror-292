import unittest
from my_package.module1 import greet

class TestGreet(unittest.TestCase):
    def test_green(self):
        self.assertEqual(greet("World"), "Hello, World!")

if __name__=="__main__":
    unittest.main()        