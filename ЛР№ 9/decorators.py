# decorators.py
from functools import wraps
from flask import request, jsonify
from jwt_factory import jwt_factory

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        user_id = jwt_factory.decode_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        kwargs['user_id'] = user_id
        return f(*args, **kwargs)
    
    return decorated
