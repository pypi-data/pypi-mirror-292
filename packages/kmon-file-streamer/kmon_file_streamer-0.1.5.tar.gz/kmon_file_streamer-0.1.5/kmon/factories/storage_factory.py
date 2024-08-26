import os

class StorageClientFactory:
    @staticmethod
    def create_client(bucket_name, context=None, credential=None):
        if StorageClientFactory.is_aws(context, credential):
            from kmon.storage.s3_client import S3Client
            return S3Client(bucket_name, credential)
        else:
            from kmon.storage.oss_client import OSSClient
            return OSSClient(bucket_name, context, credential)

    @staticmethod
    def is_aws(context, credential):
        if context:
            return hasattr(context, 'aws_request_id') or 'AWS_EXECUTION_ENV' in os.environ
        elif credential:
            return credential.oss_endpoint is None
        raise Exception("Context and credential both are null!!!")