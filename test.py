import unittest

def sum(a,b):
    return a+b

def subtract(a,b):
    return a-b

class ProblemTest(unittest.TestCase):
    def setUp(self):
        print("setup...")
        self.a= 10
        self.b= 20
    
    def test_func_1(self):
        print("test1...")
        result = sum(self.a, self.b)
        self.assertEqual(result, self.a+self.b)
        
    def test_func_2(self):
        print("test2...")
        result = subtract(self.a, self.b)
        self.assertIn(result, [-10,10])
        
    def tearDown(self):
        print("teardown...")
        self.a = 0
        self.b = 0
        
        
        
        
if __name__ == '__main__':
    unittest.main()