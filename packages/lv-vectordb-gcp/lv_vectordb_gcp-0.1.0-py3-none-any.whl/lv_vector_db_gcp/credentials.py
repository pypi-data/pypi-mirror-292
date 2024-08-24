from google.oauth2 import service_account

class Credentials:
    def __init__(self):
        pass

    def get_credentials(self,service_account_key):
        return service_account.Credentials.from_service_account_file(service_account_key)
