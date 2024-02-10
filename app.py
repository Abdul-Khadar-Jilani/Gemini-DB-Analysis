from dotenv import load_dotenv  
load_dotenv()

import streamlit as st
import os
import sqlite3

import google.generativeai as ai

ai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_users():
  conn = sqlite3.connect("example.db")  # Replace with your database name
  cur = conn.cursor()

  cur.execute("SELECT * FROM users")  # Adjust the table name if needed
  users = cur.fetchall()

  conn.close()
  return users

def get_user_by_id(user_id):
  conn = sqlite3.connect("example.db")  # Replace with your database name
  cur = conn.cursor()
  try:
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user  # Return user data as a dictionary or None if not found
  except sqlite3.Error as e:
    conn.close()
    return None

def add_user(name, age):
  """Adds a new user to the database.

  Args:
    name: Name of the user.
    age: Age of the user.
  """
  conn = sqlite3.connect("example.db")
  cur = conn.cursor()
  cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
  conn.commit()
  conn.close()

def remove_user(user_id):
    """Removes a user from the database.

    Args:
        user_id: ID of the user to be removed.
    """
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE ID=?", (user_id,))
    conn.commit()
    conn.close()

def add_column(column_name, data_type):
    """Adds a new column to the 'users' table.

    Args:
        column_name: Name of the new column.
        data_type: Data type of the new column.
    """
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute(f"ALTER TABLE users ADD COLUMN {column_name} {data_type}")
    conn.commit()
    conn.close()

def rename_column(old_column_name, new_column_name):
    """Renames a column in the 'users' table.

    Args:
        old_column_name: Current name of the column to be renamed.
        new_column_name: New name for the column.
    """
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute(f"ALTER TABLE users RENAME COLUMN {old_column_name} TO {new_column_name}")
    conn.commit()
    conn.close()

def update_data(user_id, column_name, new_value):
    """Updates the data in a specific column for a given user.

    Args:
        user_id: ID of the user whose data is to be updated.
        column_name: Name of the column to be updated.
        new_value: New value for the specified column.
    """
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {column_name} = ? WHERE ID = ?", (new_value, user_id))
    conn.commit()
    conn.close()

def get_gemini_response(question,prompt):
    model=ai.GenerativeModel(model_name="gemini-pro")
    response = model.generate_content([prompt[0],question])
    return response.text

def readsql(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        return None

prompt = [
    """you are an expert in converting English questions to SQL query!
    The SQL databse has the name example, table has the name users and following columns - ID, NAME, AGE

    for example,
    example 1 - Find the average age of all users in the database?, the sql command should something like this SELECT AVG(Age) FROM Users;

    example 2 - Find the oldest user in the database?,The sql command should be something like this SELECT * FROM users ORDER BY age DESC LIMIT 1;

    example 3 - How many users have the name John?,The sql command should look like this SELECT COUNT(*) FROM users WHERE Name='John';

    example 4 - Find the youngest user in the database,The sql command should look like this SELECT * FROM users ORDER BY age ASC LIMIT 1;

    also the sql code should not have ``` in beginning or end and sql word in the output
    """
]

# Get input from the user
question = st.text_input("Input: ", key="input")

# Submit button
submit = st.button("Ask Gemini")

if submit:
    # Get the Gemini response
    response = get_gemini_response(question, prompt)
    print(response)

    # Read the data from the database
    data = readsql(response, "example.db")

    # Display the response
    st.subheader("The response is")
    if data is not None:
        for row in data:
            print(row)
            st.header(row)
    else:
        st.error("Error retrieving data from the database.")


def show_table_data():
    # Display the response
    conn = sqlite3.connect("example.db")
    cur = conn.cursor()
    data=cur.execute("SELECT * FROM users")
    st.subheader("The response is")
    if data is not None:
        for row in data:
            print(row)
            st.header(row)
    else:
        st.error("Error retrieving data from the database.")

# Add a button to show the table data
show_button = st.button("Show Table Data")

# Show the table data when the button is clicked
if show_button:
    show_table_data()

# Add data form
st.title("Add New User")
name = st.text_input("Name:")
age = st.number_input("Age:")
add_button = st.button("Add User")

if add_button:
    try:
        add_user(name, age)
        st.success("User added successfully!")
    except sqlite3.Error as e:
        st.error(f"Error adding user: {e}")

# Remove data form
st.title("Remove User")
user_id = st.number_input("User ID:")

remove_button = st.button("Remove User")

if remove_button:
    try:
        remove_user(user_id)
        st.success("User removed successfully!")
    except sqlite3.Error as e:
        st.error(f"Error removing user: {e}")

# Add column form
st.title("Add New Column")
column_name = st.text_input("Column Name:")
data_type = st.selectbox("Data Type:", ["TEXT", "INTEGER", "REAL"])

add_column_button = st.button("Add Column")

if add_column_button:
    try:
        add_column(column_name, data_type)
        st.success("Column added successfully!")
    except sqlite3.Error as e:
        st.error(f"Error adding column: {e}")

# Rename column form
st.title("Rename Column")
old_column_name = st.text_input("Old Column Name:")
new_column_name = st.text_input("New Column Name:")

rename_column_button = st.button("Rename Column")

if rename_column_button:
    try:
        rename_column(old_column_name, new_column_name)
        st.success("Column renamed successfully!")
    except sqlite3.Error as e:
        st.error(f"Error renaming column: {e}")

# Display users


# Update data form
# st.title("Update Data")
# user_id = st.number_input("User ID:")
# column_name = st.text_input("Column Name:")
# new_value = st.text_input("New Value:")

# update_data_button = st.button("Update Data")

# if update_data_button:
#     try:
#         update_data(user_id, column_name, new_value)
#         st.success("Data updated successfully!")
#     except sqlite3.Error as e:
#         st.error(f"Error updating data: {e}")
