import tarfile, json
from io import BytesIO
from kmon.factories.storage_factory import StorageClientFactory

def kmsf_data_stream(bucket_name, file_key, context=None, credential=None, filter_map=None):
  with StorageClientFactory.create_client(bucket_name, context, credential) as client:
    file_content = client.get_file_content(file_key)
    with tarfile.open(fileobj=BytesIO(file_content), mode="r:gz") as tar:
      for file_info in tar.getmembers():
        if file_info.name.endswith('.json'):
          file_in_tar = tar.extractfile(file_info)
          for line in file_in_tar:
            obj = json.loads(line.decode('utf-8'))
            if filter_kmsf(obj, filter_map):
              yield obj

def filter_kmsf(obj, filter_map=None):
  if filter_map is not None:
    for key in filter_map:
      if obj.get(key) == filter_map[key]:
        return True
    return False
  return True
