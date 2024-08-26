import unittest
from datetime import datetime
from kmon.utility import find_latest_file
from kmon.model.credential import Credential


class TestUtilityService(unittest.TestCase):
    def test_latest_file_fetch(self):
        # credential = Credential('AKIAYW2CP6W4RG4B3IGE', '3JN0pi/ZqCAutOwRyvyVJOr1u3Z4Ti+hHtxmlF2a')
        credential = Credential('LTAI4FgNov6xmKkpGbUqNeV2', 'Ogh4Nc6MCtWVwhrDq0mTNYbM28xL9J',
                                'https://oss-cn-shanghai.aliyuncs.com')
        file_name = find_latest_file("kmon-datalake-prod", 'compress/kmon_v1_raw_specif', credential=credential)
        todayday = datetime.today().strftime('%Y-%m-%d')
        print(file_name)
        self.assertNotIn(todayday, file_name)

if __name__ == '__main__':
    unittest.main()