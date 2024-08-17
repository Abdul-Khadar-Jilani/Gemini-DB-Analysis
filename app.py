from dotenv import load_dotenv  
load_dotenv()

import streamlit as st
import os
import sqlite3

import google.generativeai as ai

ai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Database helper functions
def get_users():
    with sqlite3.connect("example.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
    return users

def add_user(name, age):
    if not name or age <= 0:
        raise ValueError("Name cannot be empty and age must be positive.")
    
    with sqlite3.connect("example.db") as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
        conn.commit()

def remove_user(user_id):
    if user_id <= 0:
        raise ValueError("User ID must be positive.")
    
    with sqlite3.connect("example.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE ID=?", (user_id,))
        conn.commit()

def add_column(column_name, data_type):
    if not column_name or not data_type:
        raise ValueError("Column name and data type cannot be empty.")
    
    with sqlite3.connect("example.db") as conn:
        cur = conn.cursor()
        cur.execute(f"ALTER TABLE users ADD COLUMN {column_name} {data_type}")
        conn.commit()

def rename_column(old_column_name, new_column_name):
    if not old_column_name or not new_column_name:
        raise ValueError("Old and new column names cannot be empty.")
    
    with sqlite3.connect("example.db") as conn:
        cur = conn.cursor()
        cur.execute(f"ALTER TABLE users RENAME COLUMN {old_column_name} TO {new_column_name}")
        conn.commit()

def update_data(user_id, column_name, new_value):
    if user_id <= 0 or not column_name or not new_value:
        raise ValueError("User ID, column name, and new value cannot be empty or negative.")
    
    with sqlite3.connect("example.db") as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE users SET {column_name} = ? WHERE ID = ?", (new_value, user_id))
        conn.commit()

def get_gemini_response(question, prompt):
    model = ai.GenerativeModel(model_name="gemini-pro")
    response = model.generate_content([prompt[0], question])
    return response.text

def readsql(sql, db):
    try:
        with sqlite3.connect(db) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
        return rows
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        return None

# Streamlit UI
title = "GenAI-DBManager"
st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)
col1, col2 = st.columns(2,gap="large")
with col1:
    st.title("Ask AI")
    prompt = [
        """you are an expert in converting English questions to SQL query!
        The SQL database is named example, the table is named users, and it has the following columns - ID, NAME, AGE.

        Example queries:
        1. Find the average age of all users in the database? => SELECT AVG(Age) FROM users;
        2. Find the oldest user in the database? => SELECT * FROM users ORDER BY age DESC LIMIT 1;
        3. How many users have the name John? => SELECT COUNT(*) FROM users WHERE name='John';
        4. Find the youngest user in the database? => SELECT * FROM users ORDER BY age ASC LIMIT 1;

        The SQL code should not include ``` at the beginning or end, and the SQL word should not be in the output.
        """
    ]

    question = st.text_input("Input:", key="input")
    submit = st.button("Ask Gemini")

    if submit:
        with st.spinner("Processing..."):
            response = get_gemini_response(question, prompt)
            st.write(f"Generated SQL: {response}")
            data = readsql(response, "example.db")

        st.subheader("The response is")
        if data:
            for row in data:
                print(row)
                st.header(row)
        else:
            st.error("Error retrieving data from the database.")
with col1:
    def show_table_data():
        with sqlite3.connect("example.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            data = cur.fetchall()
            column_names = [description[0] for description in cur.description]  # Extract column names

        st.subheader("User Table Data")
        if data:
            # Convert the data into a DataFrame-like format
            import pandas as pd
            df = pd.DataFrame(data, columns=column_names)
            st.table(df)
        else:
            st.error("No data available in the users table.")

    show_button = st.button("Show Table Data")


    #with st.expander("USER DATA"):
    if show_button:
            show_table_data()
with col2:
    def get_table_columns(table_name):
        """Get column names from a table in the database."""
        with sqlite3.connect("example.db") as conn:
            cur = conn.cursor()
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = cur.fetchall()
        return [column[1] for column in columns]  # Column names are in the second position

    def generate_input_fields(columns):
        """Generate Streamlit input fields based on table columns."""
        user_inputs = {}
        for column in columns:
            if column.lower() == "id":
                continue  # Skip the ID column
            elif column.lower() == "name":
                user_inputs[column] = st.text_input("Name:")
            elif column.lower() == "age":
                user_inputs[column] = st.number_input("Age:", min_value=0, max_value=150, step=1)
            else:
                # Assume other columns are text fields by default
                user_inputs[column] = st.text_input(f"{column.capitalize()}:")
        return user_inputs

    st.title("Add New User")

    # Get current columns from the database
    columns = get_table_columns("users")
    user_inputs = generate_input_fields(columns)

    add_button = st.button("Add User")

    if add_button:
        try:
            # Dynamically extract user inputs based on column names
            user_data = tuple(user_inputs[column] for column in columns if column.lower() != "id")
            add_user_query = f"INSERT INTO users ({', '.join(columns[1:])}) VALUES ({', '.join(['?' for _ in columns[1:]])})"
            
            # Insert the user data into the database
            with sqlite3.connect("example.db") as conn:
                cur = conn.cursor()
                cur.execute(add_user_query, user_data)
                conn.commit()
            
            st.success("User added successfully!")
        except ValueError as ve:
            st.error(f"Validation Error: {ve}")
        except sqlite3.Error as e:
            st.error(f"Database Error: {e}")


    st.title("Remove User")
    user_id = st.number_input("User ID:", min_value=0, step=1)
    remove_button = st.button("Remove User")

    if remove_button:
        try:
            remove_user(user_id)
            st.success("User removed successfully!")
        except ValueError as ve:
            st.error(f"Validation Error: {ve}")
        except sqlite3.Error as e:
            st.error(f"Database Error: {e}")

    st.title("Add New Column")
    column_name = st.text_input("Column Name:")
    data_type = st.selectbox("Data Type:", ["TEXT", "INTEGER", "REAL"])
    add_column_button = st.button("Add Column")

    if add_column_button:
        try:
            add_column(column_name, data_type)
            st.success("Column added successfully!")
        except ValueError as ve:
            st.error(f"Validation Error: {ve}")
        except sqlite3.Error as e:
            st.error(f"Database Error: {e}")

    st.title("Rename Column")
    old_column_name = st.text_input("Old Column Name:")
    new_column_name = st.text_input("New Column Name:")
    rename_column_button = st.button("Rename Column")

    if rename_column_button:
        try:
            rename_column(old_column_name, new_column_name)
            st.success("Column renamed successfully!")
        except ValueError as ve:
            st.error(f"Validation Error: {ve}")
        except sqlite3.Error as e:
            st.error(f"Database Error: {e}")

    # Update User Data
    st.title("Update User Data")
    user_id_update = st.number_input("User ID to Update:", min_value=0, step=1)
    column_name_update = st.text_input("Column Name to Update:")
    new_value_update = st.text_input("New Value:")

    update_button = st.button("Update User Data")

    if update_button:
        try:
            update_data(user_id_update, column_name_update, new_value_update)
            st.success("User data updated successfully!")
        except ValueError as ve:
            st.error(f"Validation Error: {ve}")
        except sqlite3.Error as e:
            st.error(f"Database Error: {e}")


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
