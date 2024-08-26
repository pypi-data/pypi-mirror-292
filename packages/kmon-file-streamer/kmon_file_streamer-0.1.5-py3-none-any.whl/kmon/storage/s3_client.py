import boto3
from kmon.storage.storage_client import StorageClient

class S3Client(StorageClient):
    def __init__(self, bucket_name, credential = None):
        if credential:
            session = boto3.session.Session(
                aws_access_key_id=credential.access_key,
                aws_secret_access_key=credential.secret_key
            )
            self.s3client = session.client("s3")
        else:
            self.s3client = boto3.client("s3")
        self.bucket_name = bucket_name

    def get_latest_file(self, prefix: str):
        response = self.s3client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix, MaxKeys=1)
        contents = response.get('Contents', [])
        if contents:
            return contents[0]['Key']
        return None

    def get_file_content(self, file_name):
        streamContents = self.s3client.get_object(Bucket=self.bucket_name, Key=file_name)['Body']
        return streamContents.read()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.s3client.close()