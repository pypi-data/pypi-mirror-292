class Credential:
    def __init__(self, access_key, secret_key, oss_endpoint=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.oss_endpoint = oss_endpoint