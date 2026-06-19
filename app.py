from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

DATABASE = "portfolio.db"

def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn

@app.route("/")
def home():

    conn = get_connection()

    projects = conn.execute(
        "SELECT * FROM projects"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        projects=projects
    )

if __name__ == "__main__":
    app.run(debug=True)