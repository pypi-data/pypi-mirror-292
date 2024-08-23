import os
import logging
from functools import wraps
import requests
from fastapi import HTTPException, status
from pythonjsonlogger import jsonlogger

# Configura a URL do serviço de autenticação a partir das variáveis de ambiente, com um valor padrão
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://127.0.0.1:8000/')

# Inicialização de logger
def initLog(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    log_formatter = jsonlogger.JsonFormatter('%(filename)s %(funcName)s %(lineno)s %(asctime)s %(levelname)s %(name)s %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return logger

logger = initLog(__name__)

# Decorator para verificar autenticação
def verifyauth(servico, capacidade):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Log de entrada
                logger.info(f"Args: {args}, Kwargs: {kwargs}")
                logger.info(AUTH_SERVICE_URL)
                request = kwargs.get('request')
                header = kwargs.get('header')

                # Verificação dos argumentos request e header
                if not request:
                    if len(args) > 0:
                        request = args[0]
                    else:
                        logger.error("Objeto request não encontrado.")
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request object missing")

                if not header:
                    if len(args) > 1:
                        header = args[1]
                    else:
                        logger.error("Objeto header não encontrado.")
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Header object missing")

                # Dados de autenticação
                auth_data = {
                    "username": header.security.username_token.username,
                    "password": header.security.username_token.password,
                    "service_name": servico,
                    "capacity": capacidade
                }
                
                logger.info(f"Autenticando com os dados: {auth_data}")
                AUTH_URL = AUTH_SERVICE_URL + 'auth'
                response = requests.post(AUTH_URL, json=auth_data)

                # Tratamento das respostas da autenticação
                if response.status_code == 200:
                    return await func(*args, **kwargs)
                elif response.status_code == 401:
                    logger.error(f"Falha na autenticação: {response.content}")
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
                else:
                    logger.error(f"Erro de autenticação: {response.content}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication Failed 500")
            except Exception as e:
                logger.error(f"Erro inesperado durante a autenticação: {str(e)}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado durante a autenticação")

        return wrapper
    return decorator

# Decorator para obter acesso
def GetAccess(servico):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                request = kwargs.get('request')
                header = kwargs.get('header')

                # Verificação dos argumentos request e header
                if not request:
                    if len(args) > 0:
                        request = args[0]
                    else:
                        logger.error("Objeto request não encontrado.")
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request object missing")

                if not header:
                    if len(args) > 1:
                        header = args[1]
                    else:
                        logger.error("Objeto header não encontrado.")
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Header object missing")

                # Dados de autenticação
                auth_data = {
                    "username": header.security.username_token.username,
                    "password": header.security.username_token.password,
                    "name": servico
                }

                logger.info(f"Obtendo acesso com os dados: {auth_data}")
                GET_URL = AUTH_SERVICE_URL + 'getaccess'
                response = requests.post(GET_URL, json=auth_data)

                # Tratamento das respostas de obtenção de acesso
                if response.status_code == 200:
                    return await func(*args, **kwargs)
                elif response.status_code == 401:
                    logger.error(f"Falha na autenticação: {response.content}")
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
                else:
                    logger.error(f"Erro na obtenção de acesso: {response.content}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication Failed")
            except Exception as e:
                logger.error(f"Erro inesperado durante a obtenção de acesso: {str(e)}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro inesperado durante a obtenção de acesso")

        return wrapper
    return decorator
