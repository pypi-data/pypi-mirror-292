import webbrowser
from typing import Callable
from urllib.parse import urlparse, parse_qs
import requests


class MiniOrange:
    def __init__(self, context):
        self.context = context
        self.client_id = None
        self.client_secret = None
        self.base_url = None
        self.redirect_url = None

    def set_client_id(self, client_id: str):
        self.client_id = client_id

    def set_client_secret(self, client_secret: str):
        self.client_secret = client_secret

    def set_base_url(self, base_url: str):
        self.base_url = base_url

    def set_redirect_url(self, redirect_url: str):
        self.redirect_url = redirect_url

    def start_authorization(self):
        if not all([self.client_id, self.client_secret, self.base_url, self.redirect_url]):
            return

        self.auth_url = (
            f"{self.base_url}/moas/idp/openidsso?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_url}&"  # Correct parameter name
            f"scope=openid&"  # Adjust scope as needed
            f"response_type=code&"  # Correct response type parameter
            f"state=yAwL-57K10sIIpGeVO7nR7ZAnzdsj01uGothExyVpmo"
        )
        webbrowser.open(self.auth_url)

    def handle_authorization_response(self, uri: str, callback: Callable[[str], None]):
        parsed_uri = urlparse(uri)
        if parsed_uri.path.startswith(f"{self.base_url}/lander"):
            query_params = parse_qs(parsed_uri.query)
            code = query_params.get("code", [None])[0]
            if code:
                self.request_token(code, callback)

    def request_token(self, code: str, callback: Callable[[str], None]):
        if not all([self.client_id, self.client_secret, self.base_url, self.redirect_url]):
            callback("SSO configuration is incomplete")
            return

        post_url = f"{self.base_url}/moas/rest/oauth/token"
        params = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_url,
            "code": code
        }
        try:
            response = requests.post(post_url, data=params)
            response.raise_for_status()
            data = response.json()
            id_token = data.get("id_token")
            if id_token:
                callback(id_token)
            else:
                callback("ID token not found in response")
        except requests.RequestException as e:
            callable(f"Request error:{e}")

    def fetch_user_info(self, url: str, token: str, callback: Callable[[str], None]):
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            callback(response.text)
        except requests.RequestException as e:
            callable(f"Request error : {e}")

def response_callback(result: str):
    print(result)