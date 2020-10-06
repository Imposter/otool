import re

from datetime import datetime as dt, date, time
from urllib import parse as url
from string import Template

from . import transport, origin
from lib import utils

class APISession(object):
    def __init__(self):
        """Create transport and initialize API
        """
        self._transport = transport.Transport()

        # Set a random machine hash
        self._machine_hash = utils.randint_len(19)
        self._user_id = None

        # OAuth
        self._access_token = None
        self._expires_in = None
        self._token_type = None

    @property
    def access_token(self):
        """Gets access token
        
        Returns:
            str -- API access token
        """
        return self._access_token

    @property
    def user_id(self):
        return self._user_id

    def _req_update(self, url, use_token, args, kwargs):
        req_headers = dict()
        req_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        if use_token:
            if self._access_token is not None:
                req_headers["AuthToken"] = self._access_token

            if self._machine_hash is not None:
                req_headers["X-Origin-UID"] = str(self._machine_hash)
                req_headers["X-Origin-Platform"] = "PCWIN"
        
        utils.merge_dicts(kwargs, {
            "headers": req_headers
        })

        # Update the URL and replace any placeholders
        template = Template(url)
        url = template.substitute({
            "user_id": self._user_id,
            "machine_hash": self._machine_hash,
            "access_token": self._access_token
        })

        return url

    def _get(self, url, use_token=False, *args, **kwargs):
        url = self._req_update(url, use_token, args, kwargs)
        return self._transport.get(url, *args, **kwargs)
    
    def _post(self, url, use_token=False, *args, **kwargs):
        url = self._req_update(url, use_token, args, kwargs)
        return self._transport.post(url, *args, **kwargs)

    def _auth_session(self):
        response = self._get(origin.API_AUTH_URL,
            allow_redirects=True,
            params={
                "response_type": "code",
                "client_id": origin.WEB_LOGIN_CLIENT_ID,
                "display": "originXWeb/login",
                "locale": "en_US",
                "release_type": "prod",
                "redirect_uri": "https://www.origin.com/views/login.html"
            }
        )

        return response.headers["SelfLocation"]

    def _auth_login(self, login_url, email, password, mfa_method, mfa_key_method):
        response = self._post(login_url,
            allow_redirects=True,
            data={
                "email": email, 
                "password": password,
                "_eventId": "submit",
                "cid": utils.randstr(32),
                "showAgeUp": "true",
                "googleCaptchaResponse": "",
                "thiridPartyCaptchaResponse": "",
                "_rememberMe": "off",
                "rememberMe": "off"
            }
        )
            
        login_url = response.url
        login_response = response.text

        # Check if 2FA is enabled on the account
        if re.search(r"<div class=\"tfa-container\">", login_response):
            # Get a list of all available 2FA methods
            methods = re.findall(r"name=\"codeType\" value=\"(\w+)\"", login_response)
            
            # Prompt user for selection of method
            method = mfa_method(methods)
            if method not in methods:
                raise Exception("Invalid method selected")
            
            # Select method with server
            response = self._post(login_url,
                allow_redirects=True,
                data={
                    "codeType": method, 
                    "_eventId": "submit"
                }
            )
            
            login_url = response.url

            # Get input from user and send
            security_code = mfa_key_method(method)
            response = self._post(login_url,
                allow_redirects=True,
                data={
                    "oneTimeCode": security_code,
                    "_trustThisDevice": "off",
                    "_eventId": "submit"
                }
            )

            # Update login response
            login_response = response.text

        match = re.findall(r"input type=\"hidden\" id=\"errorCode\" value=\"(\d+)\"", login_response)
        if match:
            raise Exception(f"Login error, please check your credentials: {match[0]}")
        
        match = re.findall(r"window.location = \"(\S+)\";", login_response)
        if not match:
            raise Exception("Unable to get authentication URL")

        # Complete login
        auth_url = match[0]
        response = self._get(auth_url, allow_redirects=True)
        if response.status_code != 200:
            raise Exception("Unable to complete login")

    def _auth_token(self):
        response = self._get(origin.API_AUTH_URL,
            allow_redirects=True,
            params={
                "response_type": "token",
                "client_id": origin.WEB_SDK_CLIENT_ID,
                "display": "originXWeb/login",
                "prompt": "none",
                "release_type": "prod",
                "redirect_uri": "nucleus:rest"
            }
        )

        if response.status_code != 200:
            raise Exception("Unable to get eadm_token")

        oauth_token = response.json()
        self._access_token = oauth_token["access_token"]
        self._expires_in = oauth_token["expires_in"]
        self._token_type = oauth_token["token_type"]
    
    def _auth_identify(self):
        response = self._get(origin.API_IDENTIFY_URL, 
            allow_redirects=True,
            headers={
                "Authorization": f"{self._token_type} {self._access_token}"
            })
        if response.status_code != 200:
            raise Exception("Unable to get user data")

        user_data = response.json()["pid"]
        self._user_id = user_data["pidId"]

    def login(self, email, password, mfa_method, mfa_key_method):
        location = self._auth_session()
        self._auth_login(location, email, password, mfa_method, mfa_key_method)
        self._auth_token()
        self._auth_identify()