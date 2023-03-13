
import os 

UA_OAUTH_CLIENT_ID =  os.environ.get("UA_OAUTH_CLIENT_ID")
UA_OAUTH_CLIENT_SECRET = os.environ.get("UA_OAUTH_CLIENT_SECRET")

UA_OAUTH_DOMEN = os.environ.get("UA_OAUTH_DOMEN",'https://test.id.gov.ua')


UA_OAUTH_ACCESS_TOKEN_URL = f'{UA_OAUTH_DOMEN}/get-access-token'
UA_OAUTH_USER_INFO_URL = f"{UA_OAUTH_DOMEN}/get-user-info"
UA_OAUTH_REDIRECT_URI = os.environ.get("UA_OAUTH_REDIRECT_URI",'https://rms-register.online/redirect_auth')

