import pandas as pd
import unittest
from kmon.stream.kmsf_stream import kmsf_data_stream
from kmon.model.credential import Credential
from kmon.utility import find_latest_file

credential = Credential('access-key', 'secret-key')
file_name = find_latest_file("kmon-datalake-dev2", 'compress/kmon_v1_raw_specif', credential=credential)

class TestDataStreamService(unittest.TestCase):
    def test_data_stream(self):
        count=0
        for json_obj in kmsf_data_stream("kmon-datalake-dev2", file_name, credential=credential
                     #"compress/kmon_v1_raw_specif/2024-05-30/kmon_v1_raw_specif_2024-05-30_44534.tar.gz" #750.292s
            #"compress/kmon_v1_raw_specif/2024-04-25/kmon_v1_raw_specif_2024-04-25_45222.tar.gz"#242s
            #"compress/kmon_v1_raw_specif/2024-05-27/kmon_v1_raw_specif_2024-05-27_43838.tar.gz" #344.633s
            ):
            count+=1
        print("Total count: ", count)
        self.assertTrue(True)

    def test_data_frame(self):
        count=0
        data_batch = []
        batch_size = 1000
        for json_obj in kmsf_data_stream("kmon-datalake-dev2",
                     "compress/kmon_v1_raw_specif/2024-05-30/kmon_v1_raw_specif_2024-05-30_44534.tar.gz" #805s
            #"compress/kmon_v1_raw_specif/2024-04-25/kmon_v1_raw_specif_2024-04-25_45222.tar.gz"#266s
            #"compress/kmon_v1_raw_specif/2024-05-27/kmon_v1_raw_specif_2024-05-27_43838.tar.gz" #416
                                         ):
            count+=1
            data_batch.append({
                'changedAt': json_obj.get('changedAt'),
                'source': json_obj.get('source'),
                'companyId': json_obj.get('companyId'),
                'keyId': json_obj.get('keyId')
            })
            if len(data_batch) >= batch_size:
                pd.DataFrame(data_batch)
                data_batch = []

        print("Total count: ", count)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()