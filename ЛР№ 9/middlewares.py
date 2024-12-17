from flask import request, jsonify
from functools import wraps
from models import JWTFactory
from config import SECRET_KEY

jwt_factory = JWTFactory(SECRET_KEY)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').split('Bearer ')[-1]
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        user_id = jwt_factory.decode_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        kwargs['user_id'] = user_id
        return f(*args, **kwargs)
    return decorated
