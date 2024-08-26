import json
import oss2, os
from aliyunsdkkms.request.v20160120 import GetSecretValueRequest
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkcore import client

from kmon.storage.storage_client import StorageClient

class OSSClient(StorageClient):
    def __init__(self, bucket_name, context=None, credential=None): #FIXME work with the context
        if credential :
            auth = oss2.Auth(credential.access_key, credential.secret_key)
            self.bucket_obj = oss2.Bucket(auth, credential.oss_endpoint, bucket_name)
        elif context:
            credentials = StsTokenCredential(context.credentials.accessKeyId, context.credentials.accessKeySecret,
                                             context.credentials.securityToken)
            secret_data = self.get_secrets(credentials, client, os.environ.get('secretName'), os.environ.get('secretRegion'))
            creds = context.credentials
            auth = oss2.StsAuth(creds.access_key_id, creds.access_key_secret, creds.security_token)
            self.bucket_obj = oss2.Bucket(auth, credential.oss_endpoint, bucket_name)

    def get_latest_file(self, prefix: str):
        for topic_with_prefix in oss2.ObjectIteratorV2(self.bucket_obj, prefix=prefix, max_keys=1):
            return topic_with_prefix.key
        return None

    def get_file_content(self, file_name):
        return self.bucket_obj.get_object(file_name).read()

    def get_secrets(self, credentials, client, secretName, secretRegion):
        try:
            clt = client.AcsClient(region_id=secretRegion, credential=credentials)
            request = GetSecretValueRequest.GetSecretValueRequest()
            request.set_accept_format('JSON')
            request.set_SecretName(secretName)
            request.set_VersionId("v1")
            response = json.loads(clt.do_action(request))
            secretData = response.get("SecretData")
            secretData = json.loads(secretData)
            return secretData
        except Exception as e:
            print(f"Error occurred at get secrets: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass