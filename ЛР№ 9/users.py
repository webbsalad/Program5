from flask import Blueprint, request, jsonify
from middlewares import token_required
from db import get_db_connection
from models import BonusLevelObserver

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/users/<int:id>/bonus', methods=['GET'])
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

        return jsonify({
            'id': bonus[0],
            'name': bonus[1],
            'min_spendings': bonus[2],
            'cashback_percentage': bonus[3]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
