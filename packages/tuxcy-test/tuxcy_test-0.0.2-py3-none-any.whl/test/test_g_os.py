import unittest
from test.test_common import *
from geo_auto_install.utils.g_logger import * 
from geo_auto_install.utils.g_common import * 
from geo_auto_install.utils.g_os import * 
import os


class TestGOs(unittest.TestCase):
    current_script_folder = get_current_script_dir(__file__)
    init_logger()
    
    def test_exec_command(self):
        # When
        result = exec_command(["ls","-l"])
        
        # Then
        self.assertIsNotNone(result)
        
    def test_get_files(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        
        os.makedirs(folder_path, exist_ok=True)
        filenames = ["test1.txt", "test2.txt", "test3.txt"]
        for filename in filenames:
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'w') as file:
                file.write(filename)
        
        # When
        paths = [os.path.join(folder_path, file) for file in filenames]
        files = get_files(folder_path)
        
        # Then
        self.assertSetEqual(set(files), set(paths))
        
    def test_get_files_name(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        
        os.makedirs(folder_path, exist_ok=True)
        filenames = ["test1.txt", "test2.txt", "test3.txt"]
        for filename in filenames:
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'w') as file:
                file.write(filename)
                
        # When
        files = get_files_name(folder_path)
        
        # Then
        self.assertSetEqual(set(files), set(filenames))
        
    def test_get_files_name_with_ext(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        
        os.makedirs(folder_path, exist_ok=True)
        filenames = ["test1.txt", "test2.txt", "test3.txt","test1.jar", "test2.json", "test3.ps"]
        for filename in filenames:
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'w') as file:
                file.write(filename)
        
        # When
        jar = get_files_name_with_ext(folder_path, ".jar")
        # Then
        self.assertEqual(len(jar), 1)
        self.assertEqual(jar[0], "test1.jar")
        
        # When
        json = get_files_name_with_ext(folder_path, ".json")
        # Then
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0], "test2.json")
        
        # When
        ps = get_files_name_with_ext(folder_path, ".ps")
        # Then
        self.assertEqual(len(ps), 1)
        self.assertEqual(ps[0], "test3.ps")
    
    def test_move_files_from_to(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        
        origin = os.path.join(folder_path,"origin")
        dest = os.path.join(folder_path,"dest")
        
        os.makedirs(folder_path,exist_ok=True)
        os.makedirs(origin,exist_ok=True)
        os.makedirs(dest,exist_ok=True)
        
        filenames = ["test1.txt", "test2.txt", "test3.txt"]
        for filename in filenames:
            file_path = os.path.join(origin, filename)
            with open(file_path, 'w') as file:
                file.write(filename)
        # When
        move_files_from_to(filenames,origin,dest)
        
        # Then
        dest_files = set(os.listdir(dest))        
        self.assertSetEqual(dest_files, set(filenames))
        
        # Then
        origin_files = os.listdir(origin)
        self.assertEqual(len(origin_files), 0)
    
    def test_copy_files_to(self):   
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        
        origin = os.path.join(folder_path,"origin")
        dest = os.path.join(folder_path,"dest")
        
        os.makedirs(folder_path,exist_ok=True)
        os.makedirs(origin,exist_ok=True)
        os.makedirs(dest,exist_ok=True)
        
        filenames = ["test1.txt", "test2.txt", "test3.txt"]
        for filename in filenames:
            file_path = os.path.join(origin, filename)
            with open(file_path, 'w') as file:
                file.write(filename)
        
        # When
        file_paths = [os.path.join(origin, file) for file in filenames]
        copy_files_to(file_paths, dest)
        
        # Then
        dest_files = set(os.listdir(dest))        
        self.assertSetEqual(dest_files, set(filenames))
        
        # Then
        origin = set(os.listdir(origin))        
        self.assertSetEqual(origin, set(filenames))

if __name__ == '__main__':
    unittest.main()