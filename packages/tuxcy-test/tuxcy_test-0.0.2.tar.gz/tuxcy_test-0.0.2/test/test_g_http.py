import unittest
from test.test_common import *
from geo_auto_install.utils.g_http import *


class TestGHttp(unittest.TestCase):
    current_script_folder = get_current_script_dir(__file__)
    init_logger()
    
    def test_ping(self):
        self.assertTrue(ping("https://geoservices.business-geografic.com/account/ping",{}))
        self.assertIsNone(ping("https://geoservices.fakeurl.com/test/ping",{}))
    
    def test_get_request(self):
        # Given 
        expected = "geo-account"
        
        # When
        result = execute_get_request("https://preprod-geoservices.business-geografic.com/account/version", {})
        
        # Then 
        self.assertEqual(result["serviceName"], expected)
        
    def test_post_request(self):
        # Given 
        excepted = "lucene"
        
        # When
        result = execute_post_request("http://worker0001.dev.bg.lan:10001/aas/v1/facetsMaintenance/infos", None, None, {})
        
        # Then
        self.assertEqual(result["facetEngineType"], excepted)
    
    def test_download_request(self):
        folder_path = make_test_dir(__file__, sys._getframe().f_code.co_name)
        
        # When
        target_path = os.path.join(folder_path,"test.jar")
        execute_download_request("http://regis.ciril.lan:8080/nexus/service/local/repositories/bg/content/com/bg/geo/plugin-geo-siroutier/4.1.0.GEO_2_6/plugin-geo-siroutier-4.1.0.GEO_2_6.jar", {}, target_path)
        
        # Then
        self.assertTrue(os.path.exists(target_path))
        

if __name__ == '__main__':
    unittest.main()
