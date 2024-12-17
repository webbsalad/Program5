# app.py
from flask import Flask
from router import router

app = Flask(__name__)

# Регистрация Blueprint
app.register_blueprint(router)

if __name__ == '__main__':
    app.run(debug=True)
