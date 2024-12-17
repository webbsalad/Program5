# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Инициализация приложения и базы данных
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/postgres?sslmode=disable'  # Исправленный диалект
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Определение моделей
class BonusLevel(db.Model):
    __tablename__ = 'bonus_levels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    min_spendings = db.Column(db.Float, nullable=False)
    cashback_percentage = db.Column(db.Float, nullable=False)

class UserInfo(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    passhash = db.Column(db.String(200), nullable=False)
    spendings = db.Column(db.Float, default=0)
    level_id = db.Column(db.Integer, db.ForeignKey('bonus_levels.id'))

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Регистрация Blueprint (предполагается, что router импортирован правильно)
from router import router
app.register_blueprint(router)

if __name__ == '__main__':
    app.run(debug=True)
