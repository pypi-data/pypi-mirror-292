import unittest
from test.test_common import * 
from geo_auto_install.utils.g_utils import str_to_int

class TestGUtils(unittest.TestCase):
    init_logger()

    def test_str_to_int(self):
        w1 = "1"
        self.assertEqual(str_to_int(w1), 1)
        
        w2 = "123456789"
        self.assertEqual(str_to_int(w2), 123456789)
        
        w3 = "this is a string"
        self.assertIsNone(str_to_int(w3)) 

if __name__ == '__main__':
    unittest.main()
