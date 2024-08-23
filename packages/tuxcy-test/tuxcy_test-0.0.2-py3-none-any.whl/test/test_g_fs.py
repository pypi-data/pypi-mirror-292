import unittest
from test.test_common import *
from geo_auto_install.utils.g_fs import *


class TestGFs(unittest.TestCase):
    current_script_folder = get_current_script_dir(__file__)
    init_logger()
    
    def test_safe_append(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        
        content = "blabla"
        file_path = os.path.join(folder_path, "test.txt")
        with open(file_path, 'w') as file:
                file.write(content)
        
        # Given
        excepted = f"blablableu\nblanc\nrouge\n"
        
        # When
        content2 = f'bleu\nblanc\nrouge'
        safe_append(file_path,content2)
        
        # Then
        with open(file_path, 'r') as file:
            result = file.read()
            self.assertEqual(result, excepted)    
        
    
if __name__ == '__main__':
    unittest.main()