import unittest
from datetime import datetime
from kmon.utility import find_latest_file
from kmon.model.credential import Credential


class TestUtilityService(unittest.TestCase):
    def test_latest_file_fetch(self):
        credential = Credential('access-key', 'secret-key')
        file_name = find_latest_file("kmon-datalake-dev2", 'compress/kmon_v1_raw_specif', credential=credential)
        todayday = datetime.today().strftime('%Y-%m-%d')
        print(file_name)
        self.assertNotIn(todayday, file_name)

if __name__ == '__main__':
    unittest.main()