import requests
from fastapi import HTTPException, status
from functools import wraps
import os
import logging
from pythonjsonlogger import jsonlogger

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://127.0.0.1:8000/')

def initLog(name, leve=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # log_formatter = logging.Formatter("%(filename)s %(funcName)s %(lineno)s %(asctime)s %(levelname)s %(name)s %(message)s")
    log_formatter = jsonlogger.JsonFormatter('%(filename)s %(funcName)s %(lineno)s %(asctime)s %(levelname)s %(name)s %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return logger
logger = initLog(__name__)


def verifyauth(servico, capacidade):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            header = kwargs.get('header')
            
            if not request:
                request = args[0]
            if not header:
                header = args[1]

            auth_data = {
                "username": header.security.username_token.username,
                "password": header.security.username_token.password,
                "service_name": servico,
                "capacity": capacidade
            }
            AUTH_URL = AUTH_SERVICE_URL + 'auth'
            response = requests.post(AUTH_URL, json=auth_data)
            
            if response.status_code == 200:
                return await func(*args, **kwargs)
            elif response.status_code == 401:
                logger.error(f"Falha na autenticação: {response.content}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
            else:
                logger.error(f"Falha na autenticação: {response.content}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication Failed")

        return wrapper
    return decorator

def GetAccess(servico):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            header = kwargs.get('header')
            
            if not request:
                request = args[0]
            if not header:
                header = args[1]

            auth_data = {
                "username": header.security.username_token.username,
                "password": header.security.username_token.password,
               "name": servico
            }
            GET_URL = AUTH_SERVICE_URL + 'getaccess'
            response = requests.post(GET_URL, json=auth_data)
            
            if response.status_code == 200:
                return await func(*args, **kwargs)
            elif response.status_code == 401:
                logger.error(f"Falha na autenticação: {response.content}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
            else:
                logger.error(f"Falha na autenticação: {response.content}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication Failed")

        return wrapper
    return decorator


