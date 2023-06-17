import os
import platform
import ssl

import requests
import smartsheet
import urllib3
from Utils.env_util import load_env

print("OS", platform.system(), platform.version())
print("Python", platform.python_version())
print("OpenSSL", ssl.OPENSSL_VERSION)
print("Requests", requests.__version__)
print("Urllib3", urllib3.__version__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # type: ignore

# s = requests.Session()
# s.verify = False
# try:
#     s.request("GET", "https://expired.badssl.com")
# except Exception as e:
#     print("Issue detected")
#     print(e)
# else:
#     print("Issue not detected")

# pools = s.adapters["https://"].poolmanager.pools
# key = pools.keys()[0]
# cp = pools[key]
# conn = cp._get_conn()
# print("SSLContext", conn.ssl_context.verify_mode, conn.ssl_context.check_hostname)

sheet_id = 1953997402728324
load_env()
token = os.getenv('SMARTSHEET_API_TOKEN')

ss_client = smartsheet.Smartsheet(token)
ss_client.errors_as_exceptions(True)
ss_client.Sheets.get_sheet_as_csv(
    sheet_id, "/Users/jzhang14/GitHub/jzhang14-Repos/python-misc/Modules/Learn/"
)
