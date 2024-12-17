from flask import Blueprint, request, jsonify
import bcrypt
from db import get_db_connection
from models import JWTFactory
from config import SECRET_KEY

auth_blueprint = Blueprint('auth', __name__)
jwt_factory = JWTFactory(SECRET_KEY)

@auth_blueprint.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM user_info WHERE username = %s;", (username,))
        if cursor.fetchone():
            return jsonify({'error': 'Username already exists'}), 400

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("SELECT id FROM bonus_levels ORDER BY min_spendings ASC LIMIT 1;")
        level_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO user_info (username, passhash, level_id) VALUES (%s, %s, %s) RETURNING id;", 
                       (username, hashed_password, level_id))
        user_id = cursor.fetchone()[0]
        conn.commit()

        token = jwt_factory.create_token(user_id)
        return jsonify({'token': token, 'user_id': user_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@auth_blueprint.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, passhash FROM user_info WHERE username = %s;", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode(), user[1].encode()):
            token = jwt_factory.create_token(user[0])
            return jsonify({'token': token}), 200
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
