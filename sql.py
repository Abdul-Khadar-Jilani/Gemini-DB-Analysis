import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('example.db')

# Create a cursor object
cur = conn.cursor()

# Create a table
cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER
    )
''')

# Insert some data
cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Alice', 30))
cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Bob', 25))


####print records
cur.execute("SELECT * FROM users")

# Iterate over the rows of the result
for row in cur:
    print(row)

# Commit the changes
conn.commit()

# Close the connection
conn.close()