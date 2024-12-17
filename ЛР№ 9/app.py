from flask import Flask
from auth import auth_blueprint
from users import users_blueprint

app = Flask(__name__)
app.register_blueprint(auth_blueprint)
app.register_blueprint(users_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
