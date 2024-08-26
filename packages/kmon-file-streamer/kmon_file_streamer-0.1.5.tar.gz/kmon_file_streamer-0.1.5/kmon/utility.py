from datetime import datetime, timedelta
from kmon.factories.storage_factory import StorageClientFactory

def find_latest_file(bucket_name, base_prefix, context=None, credential = None):
    start_date = datetime.today() - timedelta(days=1)
    with StorageClientFactory.create_client(bucket_name, context, credential) as client:
        while start_date >= datetime.today() - timedelta(days=365):
            date_str = start_date.strftime('%Y-%m-%d')
            prefix = f"{base_prefix}/{date_str}"

            latest_file = client.get_latest_file(prefix)
            if latest_file:
                return latest_file

            start_date -= timedelta(days=1)
    print("No files found within one year.")
    return None
