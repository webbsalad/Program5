# router.py
from flask import Blueprint, request, jsonify
import bcrypt
from db import get_db_connection
from jwt_factory import jwt_factory
from decorators import token_required
from observers import BonusLevelObserver

router = Blueprint('router', __name__)

@router.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM user_info WHERE username = %s;", (username,))
        if cursor.fetchone():
            return jsonify({'error': 'Username already exists'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor.execute("SELECT id FROM bonus_levels ORDER BY min_spendings ASC LIMIT 1;")
        bonus_level = cursor.fetchone()
        if not bonus_level:
            return jsonify({'error': 'Bonus levels not found'}), 500

        level_id = bonus_level[0]

        cursor.execute("""
            INSERT INTO user_info (username, passhash, level_id)
            VALUES (%s, %s, %s) RETURNING id;
        """, (username, hashed_password, level_id))
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


@router.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, passhash FROM user_info WHERE username = %s;", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_id, stored_hash = user
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            token = jwt_factory.create_token(user_id)
            return jsonify({'token': token}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@router.route('/users/<int:id>/bonus', methods=['GET'])
@token_required
def get_user_bonus(id, user_id):
    if id != user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT b.id, b.name, b.min_spendings, b.cashback_percentage
            FROM user_info u
            JOIN bonus_levels b ON u.level_id = b.id
            WHERE u.id = %s;
        """, (id,))
        bonus = cursor.fetchone()

        if not bonus:
            return jsonify({'error': 'Bonus level not found'}), 404

        bonus_data = {
            'id': bonus[0],
            'name': bonus[1],
            'min_spendings': bonus[2],
            'cashback_percentage': bonus[3]
        }

        return jsonify(bonus_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@router.route('/users/<int:id>/transactions', methods=['POST'])
@token_required
def add_transaction(id, user_id):
    if id != user_id:
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json()
    if not data or 'amount' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    amount = data['amount']
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'error': 'Invalid transaction amount'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, amount) VALUES (%s, %s) RETURNING id;",
            (id, amount)
        )
        transaction_id = cursor.fetchone()[0]

        cursor.execute(
            "UPDATE user_info SET spendings = spendings + %s WHERE id = %s RETURNING spendings;",
            (amount, id)
        )
        new_spendings = cursor.fetchone()[0]
        conn.commit()

        observer = BonusLevelObserver(conn)
        success, message = observer.update_bonus_level(id, new_spendings)

        response = {
            'transaction_id': transaction_id,
            'amount': amount,
            'new_spendings': new_spendings,
            'bonus_update': message
        }

        return jsonify(response), 201 if success else 400
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
