"""Authentication Module, all the logic to authenticate in PS API"""
import requests
import json
import logging  
from retry_requests import retry
from secrets_safe_library import utils, exceptions
from requests_pkcs12 import Pkcs12Adapter
import random
import string

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from urllib.parse import urlparse

TIMEOUT_CONECTION_SECONDS = 30
TIMEOUT_REQUEST_SECONDS = 30

class Authentication:
    
    _api_url = None
    _client_id = None
    _client_secret = None
    _verify_ca = True
    _token = None
    _certificate = None
    _certificate_key = None
    _sig_app_in_url = None
    _api_token = None
    _req = None
    _logger = None
    _timeout_connection_seconds = None
    _timeout_request_seconds = None
    
    def __init__(self, req, timeout_conection, timeout_request, api_url, client_id, client_secret, certificate, certificate_key, verify_ca=True, logger=None):
        
        self.validate_input("api_url", api_url)
        self.validate_input("client_id", client_id)
        self.validate_input("client_secret", client_secret)
    
        self._api_url = api_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._verify_ca = verify_ca
        self._sig_app_in_url = f"{self._api_url}/Auth/SignAppIn/"
        self._certificate = certificate
        self._certificate_key = certificate_key
        self._logger = logger
        self._timeout_connection_seconds = timeout_conection if timeout_conection else TIMEOUT_CONECTION_SECONDS
        self._timeout_request_seconds = timeout_request if timeout_request else TIMEOUT_REQUEST_SECONDS
        
        if self._certificate and self._certificate_key:
            try:
                # Using a ramdon password for pfx file
                pfx_password = ''.join(random.choices(string.ascii_lowercase, k=10))
                cert = x509.load_pem_x509_certificate(bytes(self._certificate, 'utf-8'))
                key = serialization.load_pem_private_key(bytes(self._certificate_key, 'utf-8'), None)
                
                pfx_cert = pkcs12.serialize_key_and_certificates(
                    name=b"bt_certificate",
                    key=key,
                    cert=cert,
                    cas=None,
                    encryption_algorithm=serialization.BestAvailableEncryption(bytes(pfx_password, 'utf-8'))
                )
                
                parsed_url = urlparse(self._api_url)
                port_segment = f":{parsed_url.port}" if parsed_url.port else ""
                url = f"{parsed_url.scheme}://{parsed_url.hostname}{port_segment}"
                
                # checking if pfx certificate is a valid certificate
                req.mount(url, Pkcs12Adapter(pkcs12_data=pfx_cert, pkcs12_password=pfx_password))
            except:
                raise exceptions.AuthenticationFailure(f"Error using client certificate and certificate key. Please try again with a new client certificate.")
        
        
        utils.print_log(self._logger, f"How long to wait for the server to connect and send data before giving up: connection timeout: {self._timeout_connection_seconds} seconds, request timeout {self._timeout_request_seconds} seconds", logging.DEBUG)
        
        self._req = req

        if not self._verify_ca:
            utils.print_log(self._logger, "verify_ca=false is insecure, it instructs the caller to not verify the certificate authority when making API calls.", logging.WARNING)
            self._req.verify = False

        
    def oauth(self):

        """
        Get API Token
        Arguments:
            Client Id
            Secret
        Returns:
            Token
        """

        endpoint_url = self._api_url + "/Auth/connect/token"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        auth_info = {
            'client_id' : self._client_id,
            'client_secret' : self._client_secret,
            'grant_type' : 'client_credentials'
        }
  
        with requests.Session() as session:
            # This call needs to use another request object to be able to call API with appended certificate.
            oauth_req = retry(session, retries=3, backoff_factor=0.2, status_to_retry=(400,408,500,502,503,504))
            response = oauth_req.post(endpoint_url, auth_info, header, verify=self._verify_ca, timeout=(self._timeout_connection_seconds, self._timeout_request_seconds))
        del oauth_req
        del session
        return response

    
    def sign_app_in(self):
        """
        Sign in to Secret safe API
        Arguments:
        Returns:
            logged user
        """

        utils.print_log(self._logger, f"Calling sign_app_in endpoint: {self._api_url}", logging.INFO)
        return self.send_post_sign_app_in()


    def get_api_access(self):
        """
        Get API Access
        Arguments:
        Returns:
            Result of sign_app_in call
        """

        oauth_response = self.oauth()

        if oauth_response.status_code != 200:
            raise exceptions.AuthenticationFailure(f"Error getting token, message: {oauth_response.text}, statuscode: {oauth_response.status_code}")
                        
        token_object=json.loads(oauth_response.text)
        self._api_token = token_object['access_token']
        return self.sign_app_in()

    def sign_app_out(self):
        """
        Sign out to Secret safe API
        Arguments:
        Returns:
            Status of the action
        """
        url = f"{self._api_url}/Auth/Signout"
        utils.print_log(self._logger, f"Calling sign_app_out endpoint: {url}", logging.DEBUG)
        
        # Connection : close - tells secrets safe to close the session.
        response = self._req.post(url, timeout=(self._timeout_connection_seconds, self._timeout_request_seconds))
        if response.status_code == 200:
            return True

        
    def send_post_sign_app_in(self):
        """
        Send Post request to Sign app in service
        Arguments:
        Returns:
            Service URL
            Certificate
        """
        
        headers = {'Authorization': f'Bearer {self._api_token}'}
        response = self._req.post(self._sig_app_in_url, headers=headers, timeout=(self._timeout_connection_seconds, self._timeout_request_seconds))
        del self._api_token
        return response


    def validate_input(self, parameter_name, parameter_value):
        """
        Validate input
        Arguments:
            Parameter name
            Parameter Value
        Returns:
        """
        if not parameter_value:
            raise exceptions.OptionsError(f"{parameter_name} parameter is missing")
        
        if parameter_name.lower() == "api_url":
            try:
                parsed_url = urlparse(parameter_value)
                all([parsed_url.scheme, parsed_url.netloc]) 
            except:
                raise exceptions.OptionsError(f"Url {parameter_value} is not valid, please check format")
