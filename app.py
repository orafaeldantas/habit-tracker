from flask import Flask
from database import get_db

app = Flask(__name__)



@app.route('/')
def hello():
    cur = get_db().cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (1,))
    user_data = cur.fetchone()
    print(f'teste {user_data}')

    
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)

    