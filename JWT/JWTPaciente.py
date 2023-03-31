import datetime
from cryptography.hazmat.primitives import serialization
import jwt
from pathlib import Path
from time import sleep

class JWT:
    def __init__(self) -> None:
        self.__Path_SSH = str(Path(__file__).parent / '.ssh')
        self.__private_key = open(f'{self.__Path_SSH}/paciente', 'r').read()
        self.__priKey = serialization.load_ssh_private_key(self.__private_key.encode(), password=b'L0g1nP4c13nt3')
        self.__public_key = open(f'{self.__Path_SSH}/paciente.pub', 'r').read()
        self.__pubKey = serialization.load_ssh_public_key(self.__public_key.encode())
    def new_token(self):
        payload_data = {
            'sub': 'paciente',
            'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=3) #10 minutos de acesso
        }
        token = jwt.encode(
            payload_data,
            self.__priKey,
            'RS256'
        )
        return token
    
    def _validation_token(self, token:str):
        try:
            jwt.decode(token, self.__public_key, ['RS256', ])
            return ('Success', True)
        except jwt.InvalidSignatureError as e:
            return (f'ERROR -> Signature is invalid', False)
        except jwt.ExpiredSignatureError as e:
            return (f'ERROR -> Signature has expired', False)

if __name__ == '__main__':
    j = JWT()
    token = j.new_token()