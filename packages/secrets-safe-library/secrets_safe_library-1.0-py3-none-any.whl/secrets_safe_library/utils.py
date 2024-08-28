"""Utils module"""
import logging
from secrets_safe_library import exceptions

def print_log(logger, log_message, level):
    """
    Print a log message
    Arguments:
        Logger
        Log level
        Log message
    Returns:
    """
    if logger:
        if level == logging.DEBUG:
            logger.debug(log_message)
        elif level == logging.INFO:
            logger.info(log_message)
        elif level == logging.ERROR:
            logger.error(log_message)
        elif level == logging.WARN:
            logger.warning(log_message)
            
            
def prepare_certificate_info(certificate, certificate_key):
    """
    Validate certificate and certificate key
    Arguments:
        certificate
        certificate_key
    Returns:
        certificate
        certificate_key
        
    """
    
    if certificate and certificate_key:
        
        if "BEGIN CERTIFICATE" not in certificate:
            raise exceptions.OptionsError("Bad certificate content")
        
        if "BEGIN PRIVATE KEY" not in certificate_key:
            raise exceptions.OptionsError("Bad certificate key content")
        
        certificate = certificate.replace(r'\n', '\n')
        certificate_key = certificate_key.replace(r'\n', '\n')

        certificate = f"{certificate}\n"
        certificate_key = f"{certificate_key}\n"
        
        return certificate, certificate_key
    
    return "", ""