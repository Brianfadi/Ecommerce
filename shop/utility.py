# utility.py


CONSUMER_KEY = "n3bx18XFBgrSc7CIROHss6aMO9anA21l2Pqw2toGA3GrHpgY"
CONSUMER_SECRET = "Ph6DqDN8q5N7EMqFQIc8nKq1yrum4GYdmgkKsXAT8hXBMPQgIEfuvNxgqTkWpHX9"
BASE_URL = "https://sandbox.safaricom.co.ke"
SHORTCODE = "174379"
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"



# Optional: Add utility functions for generating tokens, handling requests, etc.
def get_access_token():
    """Fetch access token from Safaricom API."""
    import requests
    from requests.auth import HTTPBasicAuth

    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to get access token", response.json())
