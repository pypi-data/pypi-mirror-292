import unittest
import shutil
from test.test_common import * 
from geo_auto_install.geo_versions import *

class TestGVersions(unittest.TestCase):
    current_script_folder = get_current_script_dir(__file__)
    init_logger()

    def test_fetch_current_geo_version(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        apps_folder = os.path.join(folder_path, "apps")
        os.makedirs(apps_folder, exist_ok=True)
        
        
        version_file = os.path.join(apps_folder, "version.geo") 
        with open(version_file, 'w') as file:
                file.write("2.5.6")
        
        context = {}
        context[CTX_PROP_GEO_INSTALL_PATH] = folder_path
        
        fetch_current_geo_version(context, action=None)
        
        expected = {
                    "geo" : {
                         "current": "2.5.6" 
                         }
                    }
        
        self.assertDictEqual(expected, context[CTX_PROP_GEO_VERSIONS])
        
    def test_negociate_new_geo_version_last_patch(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
    
        shutil.copy(os.path.join(self.current_script_folder, "resources/versions_file.json"), folder_path)
        
        # Geo version classic negociation 
        context = {}
        context[CTX_PROP_GEO_VERSIONS_FILE] = os.path.join(folder_path, "versions_file.json") 
        context[CTX_PROP_NEGOCIATION_MODE] = "LAST_PATCH"
        context[CTX_PROP_GEO_VERSIONS] = {
                    "geo" : {
                         "current": "2.5.2" 
                         }
                    }
        negociate_new_geo_version(context, action=None)
        self.assertEqual("2.5.7", context[CTX_PROP_GEO_VERSIONS]["geo"]["next"])
        
        # Geo version negociation when the current version is the last minor 
        context2 = {}
        context2[CTX_PROP_GEO_VERSIONS_FILE] = os.path.join(folder_path, "versions_file.json") 
        context2[CTX_PROP_NEGOCIATION_MODE] = "LAST_PATCH"
        context2[CTX_PROP_GEO_VERSIONS] = {
                    "geo" : {
                         "current": "2.5.7" 
                         }
                    }
        negociate_new_geo_version(context2, action=None)
        self.assertEqual("2.5.7", context2[CTX_PROP_GEO_VERSIONS]["geo"]["next"])
    
    def test_negociate_new_geo_version_last_minor(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
    
        shutil.copy(os.path.join(self.current_script_folder, "resources/versions_file.json"), folder_path)
        
        # Geo version classic negociation 
        context = {}
        context[CTX_PROP_GEO_VERSIONS_FILE] = os.path.join(folder_path, "versions_file.json") 
        context[CTX_PROP_NEGOCIATION_MODE] = "LAST_MINOR"
        context[CTX_PROP_GEO_VERSIONS] = {
                    "geo" : {
                         "current": "2.5.2" 
                         }
                    }
        negociate_new_geo_version(context, action=None)
        self.assertEqual("2.7.0", context[CTX_PROP_GEO_VERSIONS]["geo"]["next"])
    
    def test_negociate_new_geo_version_last_major(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
    
        shutil.copy(os.path.join(self.current_script_folder, "resources/versions_file.json"), folder_path)
        
        # Geo version classic negociation 
        context = {}
        context[CTX_PROP_GEO_VERSIONS_FILE] = os.path.join(folder_path, "versions_file.json") 
        context[CTX_PROP_NEGOCIATION_MODE] = "LAST_MAJOR"
        context[CTX_PROP_GEO_VERSIONS] = {
                    "geo" : {
                         "current": "1.5.0" 
                         }
                    }
        negociate_new_geo_version(context, action=None)
        self.assertEqual("2.7.0", context[CTX_PROP_GEO_VERSIONS]["geo"]["next"])
    
    def test_fetch_new_geo_solutions_versions(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        
        shutil.copy(os.path.join(self.current_script_folder, "resources/versions_file.json"), folder_path)
        
        context = {}
        context[CTX_PROP_GEO_VERSIONS_FILE] = os.path.join(folder_path, "versions_file.json") 
        context[CTX_PROP_GEO_VERSIONS] = {
                    "geo" : {
                            "current": "2.5.2",
                            "next": "2.5.7"
                         }
                    }
        
        expected = {
                        "geo" : {
                            "current": "2.5.2",
                            "next": "2.5.7"
                         },
                        "plugin-solutions-backoffice" : {
                            "current": "2.5.1.GEO_2_5",
                            "next": "2.5.5.GEO_2_5"
                        },
                        "plugin-sol-import" : {
                            "current": "1.6.0.GEO_2_5",
                            "next": "1.6.1.GEO_2_5"
                        },
                        "geo-spac-plugin" : {
                            "current": "2.5.0.GEO_2_5",
                            "next": "2.5.0.GEO_2_5"
                        },
                        "geo-cartads" : {
                            "current": "2.12.0.GEO_2_5",
                            "next": "2.12.0.GEO_2_5"
                        }
                    }
        
        input_children = [
                {
                    "version": "2.5.1.GEO_2_5",
                    "name": "GEO plugin for GEO Solutions backoffice"
                },
                {
                    "version": "1.6.0.GEO_2_5",
                    "name": "Plugin Import"
                },
                {
                    "version": "2.5.0.GEO_2_5",
                    "name": "geo-spac-plugin"
                },
                {
                    "version": "2.12.0.GEO_2_5",
                    "name": "geo-cartads"
                }
            ]
        fetch_new_geo_solutions_versions(context, input_children)
        
        self.assertDictEqual(expected, context[CTX_PROP_GEO_VERSIONS])

if __name__ == '__main__':
    unittest.main()