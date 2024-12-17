import jwt
import datetime
from psycopg2 import sql

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
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

class BonusLevelObserver:
    def __init__(self, db_conn):
        self.conn = db_conn

    def update_bonus_level(self, user_id, new_spendings):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT level_id FROM user_info WHERE id = %s;", (user_id,))
            current_level_id = cursor.fetchone()[0]

            cursor.execute("""
                SELECT id FROM bonus_levels
                WHERE min_spendings <= %s
                ORDER BY min_spendings DESC
                LIMIT 1;
            """, (new_spendings,))
            new_level_id = cursor.fetchone()[0]

            if new_level_id != current_level_id:
                cursor.execute("UPDATE user_info SET level_id = %s WHERE id = %s;", (new_level_id, user_id))
                self.conn.commit()
                return True, 'Bonus level updated'
            return True, 'No change in bonus level'
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
