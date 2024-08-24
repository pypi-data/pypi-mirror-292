from abc import ABC, abstractmethod

class StorageClient(ABC):
    @abstractmethod
    def get_latest_file(self, prefix: str):
        pass

    @abstractmethod
    def get_file_content(self, file_name):
        pass