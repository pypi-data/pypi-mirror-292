"""SecretsSafe Module, all the logic to retrieve secrets from PS API"""

from secrets_safe_library import secrets, utils, exceptions
import logging
import requests

class SecretsSafe(secrets.Secrets):
    
    _authentication = None
    _logger = None
    _separator = None
    
    def __init__(self, authentication, logger=None, separator="/"):
        self._authentication = authentication
        self._logger = logger
        
        if len(separator.strip()) != 1:
            raise exceptions.LookupError(f"Invalid separator: {separator}")
        self._separator = separator


    def get_secret(self, path):
        """
        Get secret by path
        Arguments:
            path
        Returns:
            Retrieved secret string
        """
        
        utils.print_log(self._logger, "Running get_secret method in SecretsSafe class", logging.DEBUG)
        secrets_dict = self.secrets_by_path_flow([path])
        return secrets_dict[path]


    def get_secrets(self, paths):
        """
        Get secrets by paths
        Arguments:
            paths list
        Returns:
            Retrieved secret in dict format
        """

        utils.print_log(self._logger, "Running get_secrets method in SecretsSafe class", logging.INFO)
        secrets_dict = self.secrets_by_path_flow(paths)
        return secrets_dict
        

    def secrets_by_path_flow(self, paths):
        """
        Secrets by path flow
        Arguments:
            paths list
        Returns:
            Response (Dict) 
        """

        response = {}
        for path in paths:
            
            if not path:
                continue

            utils.print_log(self._logger, f"**************** secret path: {path} *****************", logging.INFO)

            data = path.split(self._separator)
            
            if len(data) < 2:
                raise exceptions.LookupError(f"Invalid secret path: {path}, check your path and title separator, separator must be: {self._separator}")

            folder_path = data[:-1]
            title = data[-1]
            
            secret_response = self.get_secret_by_path(self._separator.join(folder_path), title, self._separator)
    
            if secret_response.status_code != 200:
                if not self._authentication.sign_app_out():
                    utils.print_log(self._logger, "Error in sign_app_out", logging.ERROR)
                raise exceptions.LookupError(f"Error getting secret by path, message: {secret_response.text}, statuscode: {secret_response.status_code}")
            
            secret = secret_response.json()

            if secret:
                utils.print_log(self._logger, f"Secret type: {secret[0]['SecretType']}", logging.DEBUG)
                
                if secret[0]['SecretType'] == "File":
                    utils.print_log(self._logger, "Getting secret by file", logging.DEBUG)
                    file_response = self.get_file_by_id(secret[0]['Id'])
                    
                    if file_response.status_code != 200:
                        if not self._authentication.sign_app_out():
                            utils.print_log(self._logger, "Error in sign_app_out", logging.ERROR)
                        raise exceptions.LookupError(f"Error getting file by id, message: {file_response.text}, statuscode: {file_response.status_code}")

                    response[path] = file_response.text
                else:
                    response[path] = secret[0]['Password']

                utils.print_log(self._logger, "Secret was successfully retrieved", logging.INFO)
            else:
                raise exceptions.LookupError(f"{path}, Secret was not found")
        
        return response
         

    def get_secret_by_path(self, path, title, separator, send_title=True):
        """
        Get secrets by path and title
        Arguments:
            Secret Path
            Secret Title
        Returns:
            Secret 
        """

        url = f"{self._authentication._api_url}/secrets-safe/secrets?path={path}&separator={separator}"

        if send_title:
            url = f"{self._authentication._api_url}/secrets-safe/secrets?title={title}&path={path}&separator={separator}"

        utils.print_log(self._logger,  f"Calling get_secret_by_path endpoint: {url}", logging.DEBUG)
        response = self._authentication._req.get(url, timeout=(self._authentication._timeout_connection_seconds, self._authentication._timeout_request_seconds))
        return response
    

    def get_file_by_id(self, secret_id):
        """
        Get a File secret by File id
        Arguments:
            secret id
        Returns:
            File secret text
        """

        url = f"{self._authentication._api_url}/secrets-safe/secrets/{secret_id}/file/download"
        utils.print_log(self._logger,  f"Calling get_file_by_id endpoint: {url}", logging.DEBUG)
        response = self._authentication._req.get(url, timeout=(self._authentication._timeout_connection_seconds, self._authentication._timeout_request_seconds))
        return response