
import json
import urllib.parse
import http.client
from django.shortcuts import redirect, render
from django.http import HttpResponse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import jwt
#import logging

#logger = logging.getLogger(__name__)

class OAuthManager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://v.xecurify.com/moas/idp/openidsso"
        self.redirect_uri = 'http://127.0.0.1:8000/auth/callback/'

    def oauth_login(self, request):
        payload = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'email',
            'response_type': 'code',
            'state': 'axylkijhgfvbmx675756756'
        }
        query_string = urllib.parse.urlencode(payload)
        url = f"{self.base_url}?{query_string}"
        #logger.info("Redirecting to URL: %s", url)
        return redirect(url)

    def xecurify_callback(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        request.session['user_name'] = 'v'

        if code and state:
            response_content = f"Authorization Code: {code}, State: {state}"
            #logger.info("Received authorization code")
        else:
            response_content = "Missing authorization code or state parameter."
            #logger.error("Missing authorization code or state parameter.")

        conn = http.client.HTTPSConnection('v.xecurify.com')

        payload = urllib.parse.urlencode({
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'http://127.0.0.1:8000/auth/idtoken/',
            'scope': 'email openid profile',
            'code': code
        })

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            conn.request('POST', '/moas/rest/oauth/token', body=payload, headers=headers)
            response = conn.getresponse()
            if response.status == 200:
                response_body = response.read().decode()
                result = json.loads(response_body)
                #logger.info("Received ID token")
            else:
                result = {'error': f"Failed with status code {response.status}"}
                #logger.error("Failed to get ID token")
        except Exception as e:
            result = {'error': str(e)}
            #logger.error("Exception occurred: %s", str(e))
        finally:
            conn.close()

        token = result.get('id_token')

        certificate ="""
        -----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzIKQ+V528e3nGaOL72XA
        avmL2HAXwdG5+0Cg2X+ezPfSn2U+DxbYOKFyHXfdCj4ocgF1MKk1ECUDhMlZ6vsl
        m7ZPuq9Nus6cYeBxSFdKXaC+vI0hpghkGwAl7a6YT4HAbZ3qs+T7My5gaeuXI1j+
        8KBOXK8VRDormzQlI0Q+qbfqUSMCNBMsknxFWfgxvvXSBqEOV2Yq0hbp+JSrsB1S
        9DefmvNmxUKLDQ65MmInZ7HqfE+ocWt6H0ba9zISCgjSEs4m0fY6fr99EhuQ9vKX
        GcxQfvu2qAOHz0te4yQ67xoUGWzMCmZG3TUTfYz+kFVCSJSrmSnTzkppffio7ooA
        owIDAQAB
        -----END PUBLIC KEY-----
        """

        public_key = serialization.load_pem_public_key(certificate.encode(), backend=default_backend())

        try:
            decoded_token = jwt.decode(token, public_key, algorithms=["RS256"], audience=self.client_id, leeway=60)
            #logger.info("Token is valid. Decoded payload: %s", decoded_token)
            return decoded_token
        except jwt.ExpiredSignatureError:
            #logger.error("Token has expired.")
            return HttpResponse("Token expired")
        except jwt.InvalidTokenError:
            #logger.error("Invalid token.")
            return HttpResponse("Invalid token")
