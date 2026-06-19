import sqlite3

conn = sqlite3.connect("portfolio.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS projects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    technologies TEXT,
    github TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    message TEXT
)
""")

cursor.execute("DELETE FROM projects")

projects = [

(
    "Smart Age Calculator",

    "A responsive Flask web application that calculates age accurately and stores user history using SQLite database.",

    "Python, Flask, HTML, CSS, JavaScript, SQLite",

    "https://github.com/sravanthi9392-hub/SmartAgeCalculator"
),

(
    "Smart Healthcare System",

    "Healthcare management platform with authentication, patient registration and health record management.",

    "Python, Flask, SQLite",

    "https://github.com/sravanthi9392-hub/SmartAgeCalculator"
),

(
    "Network Monitoring System",

    "Network utility application providing DNS lookup, host monitoring and port scanning features.",

    "Python, Flask, Networking",

    "https://github.com/sravanthi9392-hub/Network-Monitoring-System"
)

]

cursor.executemany(
"""
INSERT INTO projects
(title,description,technologies,github)
VALUES(?,?,?,?)
""",
projects
)

conn.commit()
conn.close()

print("Database Created Successfully")