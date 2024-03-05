import unittest
from utils import guess2color

class colors_test(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(guess2color("crane", "grace"), "XGGYG")
    
    def test_duplicate(self):
        self.assertEqual(guess2color("child", "couch"), "GXXXY")

if __name__ == "__main__":
    unittest.main()
