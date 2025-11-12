import logging, os
from flask import Flask, g
from datetime import timedelta
from dotenv import load_dotenv
from database import init_db
from routes import auth_bp, habits_bp



load_dotenv()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["DATABASE"] = os.path.join(BASE_DIR, "habit-tracker.db")

app.register_blueprint(auth_bp)
app.register_blueprint(habits_bp)

with app.app_context():
    init_db()


# Close db - More security
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        logging.info("Database connection closed.")




if __name__ == '__main__':
    app.run(debug=True)

    