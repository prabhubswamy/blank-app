import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os

# Database setup
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            task TEXT,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_task(task, category):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (date, task, category) VALUES (?, ?, ?)", 
                   (datetime.now().strftime("%Y-%m-%d"), task, category))
    conn.commit()
    conn.close()

def get_tasks(start_date, end_date):
    conn = sqlite3.connect('tasks.db')
    query = "SELECT * FROM tasks WHERE date BETWEEN ? AND ?"
    tasks = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return tasks

# Initialize database
init_db()

st.set_page_config(
    layout= "wide")
# Streamlit app
st.title("Task Tracker & Retrieve Summary App")

# Input section
st.header("Add a New Task")

# Initialize session state for inputs
if "task_input" not in st.session_state:
    st.session_state["task_input"] = ""
if "task_category" not in st.session_state:
    st.session_state["task_category"] = "Regular"

task_input = st.text_area("Enter your task:", value=st.session_state["task_input"], placeholder="Describe the task you achieved...")
task_category = st.selectbox("Select Task Category", ["Regular", "Adhoc Report","Automation"],index=0)

if st.button("Add Task"):
    if task_input.strip() and task_category:
        add_task(task_input.strip(), task_category)
        st.success("Task added successfully!")

        # Clear the input fields
        st.session_state["task_input"] = ""
        st.session_state["task_category"] = "Regular"
    else:
        st.warning("Please enter a task description.")

# Summary section
st.sidebar.title("Retrieve Task Summary")
summary_type = st.sidebar.selectbox("Select Summary Range", ["Last 15 days", "Monthly", "Quarterly", "Custom Range"])

# Date selection based on summary type
if summary_type == "Last 15 days":
    start_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
elif summary_type == "Monthly":
    start_date = (datetime.now().replace(day=1)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
elif summary_type == "Quarterly":
    month = datetime.now().month
    quarter_start_month = month - (month - 1) % 3
    start_date = datetime(datetime.now().year, quarter_start_month, 1).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
elif summary_type == "Custom Range":
    start_date = st.date_input("Start Date").strftime("%Y-%m-%d")
    end_date = st.date_input("End Date").strftime("%Y-%m-%d")

# Fetch and display tasks
if st.sidebar.button("Retrieve Summary"):
    tasks = get_tasks(start_date, end_date)
    if not tasks.empty:
        st.write(f"### Task Summary ({start_date} to {end_date})")
        for _, row in tasks.iterrows():
            st.write(f"- **{row['date']}**: {row['task']}")

        # Export to CSV
        csv = tasks.to_csv(index=False)
        b64 = st.download_button(
            label="Download Summary as CSV",
            data=csv,
            file_name=f"task_summary_{start_date}_to_{end_date}.csv",
            mime="text/csv",
        )

    else:
        st.write("No tasks found in this period.")

st.write("Use this summary at the time of performance review for an overview of your accomplishments.")


