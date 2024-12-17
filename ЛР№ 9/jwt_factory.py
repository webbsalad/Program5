# jwt_factory.py
import jwt
import datetime
from config import Config

class JWTFactory:
    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_token(self, user_id, expiration_minutes=60):
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expiration_minutes)
        payload = {
            'user_id': user_id,
            'exp': expiration_time
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

jwt_factory = JWTFactory(Config.SECRET_KEY, Config.JWT_ALGORITHM)
