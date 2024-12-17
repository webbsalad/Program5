# observers.py
from db import get_db_connection

class BonusLevelObserver:
    def __init__(self, db_conn):
        self.conn = db_conn

    def update_bonus_level(self, user_id, new_spendings):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT level_id FROM user_info WHERE id = %s;", (user_id,))
            result = cursor.fetchone()
            if not result:
                return False, 'User not found'
            current_level_id = result[0]

            cursor.execute("""
                SELECT id, name, min_spendings, cashback_percentage
                FROM bonus_levels
                WHERE min_spendings <= %s
                ORDER BY min_spendings DESC
                LIMIT 1;
            """, (new_spendings,))
            new_level = cursor.fetchone()

            if not new_level:
                return False, 'No suitable bonus level found'

            new_level_id = new_level[0]

            if new_level_id != current_level_id:
                cursor.execute("UPDATE user_info SET level_id = %s WHERE id = %s;", (new_level_id, user_id))
                self.conn.commit()
                return True, 'Bonus level updated'
            else:
                return True, 'No change in bonus level'
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
        finally:
            cursor.close()
