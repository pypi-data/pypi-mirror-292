import unittest
from test.test_common import * 
from geo_auto_install.geo_update import *

class TestGUpdate(unittest.TestCase):
    current_script_folder = get_current_script_dir(__file__)
    init_logger()
        
    def test_remplace_geo_solutions_artefacts(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        extensions_path = os.path.join(folder_path, "extensions")
        new_extensions_path = os.path.join(folder_path, "new_extensions")
        
        os.makedirs(folder_path, exist_ok=True)
        os.makedirs(extensions_path, exist_ok=True)
        os.makedirs(new_extensions_path, exist_ok=True)
        
        f1 = ["old-plugin1.jar","old-plugin2.jar"]
        f2 = ["new-plugin1.jar","new-plugin2.jar"]
        
        for filename in f1:
            file_path = os.path.join(extensions_path, filename)
            with open(file_path, 'w') as file:
                file.write(filename)
        
        for filename in f2:
            file_path = os.path.join(new_extensions_path, filename)
            with open(file_path, 'w') as file:
                file.write(filename)
        
        context = {}
        context[CTX_PROP_GEO_EXTENSIONS_PATH] = extensions_path
        context[CTX_PROP_GEO_EXTENSIONS_TEMP_PATH] = new_extensions_path
        
        # When
        self.assertTrue(remplace_geo_solutions_artefacts(context, action=None))
        
        # Then
        new_extensions_path_files = set(os.listdir(new_extensions_path))        
        self.assertSetEqual(new_extensions_path_files, set(f1 + f2))
        
        # Then
        extensions_path_files = set(os.listdir(extensions_path))        
        self.assertSetEqual(extensions_path_files, set(f2))
        
        
if __name__ == '__main__':
    unittest.main()