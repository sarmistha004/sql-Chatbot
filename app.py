import streamlit as st
import mysql.connector
import openai
import os

# 🔐 Load OpenAI API key (from env or Streamlit secrets)
openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host='sql12.freesqldatabase.com',
    port=3306,
    user='sql12787470',
    password='Tbsv7vtsVi',
    database='sql12787470'
)
cursor = conn.cursor()

# ✅ Get table schema
def get_schema(cursor):
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    schema = {}
    for (table_name,) in tables:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        schema[table_name] = [col[0] for col in columns]
    return schema

# ✅ Generate SQL using GPT
def generate_sql_query(user_question, schema_dict):
    schema_str = ""
    for table, cols in schema_dict.items():
        schema_str += f"Table {table} has columns: {', '.join(cols)}\n"

    db_name = "sql12787470"

    prompt = f"""
You are an expert SQL assistant working with a MySQL database named `{db_name}`. Based on the schema below, write a SQL query to answer the user's question.
Only return the SQL query without explanation.

When filtering strings in WHERE clause, always use:
LOWER(TRIM(column)) LIKE LOWER('%value%') 

Here is the database schema:
{schema_str}

User question: {user_question}
SQL query:
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().strip("`")

# ✅ Execute SQL and return formatted response
def execute_sql_and_respond(sql_query):
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if not results:
            return "🤷 No data found for your query."

        response = "📊 Result:\n"
        for row in results:
            response += " • " + ", ".join(str(i) for i in row) + "\n"
        return response.strip()

    except Exception as e:
        return f"❌ SQL Error: {str(e)}"

# ✅ Streamlit UI
st.set_page_config(page_title="DataWhiz - SQL Chatbot", layout="centered")

# ✅ Hide UI elements and style enhancements
hide_streamlit_ui = """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .css-15zrgzn {display: none;}
    textarea {
        font-size: 18px !important;
        padding: 10px !important;
        min-height: 120px !important;
    }
    </style>
"""
st.markdown(hide_streamlit_ui, unsafe_allow_html=True)

# ✅ Title and intro
st.markdown("""
    <h1 style='font-size: 40px; color:#6C63FF;'>🤖 <span style="font-family:monospace;">DataWhiz</span> 🌛</h1>
    <p style='font-size: 22px; font-weight: bold;'>Ask anything about your MySQL database below:</p>
""", unsafe_allow_html=True)

# ✅ Example dropdown
examples = [
    "How many users are older than 30?",
    "List all users registered in June",
    "Count of users named Riya",
    "What are the email addresses of users under 25?"
]

example_choice = st.selectbox("🔹 Choose an example question (optional):", ["--- Select ---"] + examples)

# ✅ Input Area
user_question = st.text_area(
    label="Your SQL Question",
    label_visibility="collapsed",
    height=120,
    placeholder="Type your SQL-related question here...",
    key="user_input_box",
    value=example_choice if example_choice != "--- Select ---" else ""
)

# ✅ Buttons
col1, col2 = st.columns([1, 1])
submit = col1.button("🤮 Search")
clear = col2.button("❌ Clear")

# ✅ Logic
if clear:
    st.experimental_rerun()

if submit:
    user_input = user_question.strip().lower()

    if user_input == "":
        st.warning("⚠️ Please enter a valid question.")

    elif user_input in ["hi", "hello", "hey"]:
        st.markdown("<p style='font-size:24px; color:green;'>👋 <b>Hello!</b> How can I help you?</p>", unsafe_allow_html=True)

    elif "thank" in user_input:
        st.markdown("<p style='font-size:24px; color:#2E8B57;'>🙏 You're welcome! I'm always here to help you when you need.</p>", unsafe_allow_html=True)

    else:
        schema = get_schema(cursor)
        with st.spinner("⏳ Generating and executing SQL query..."):
            sql = generate_sql_query(user_question, schema)
            answer = execute_sql_and_respond(sql)
            st.markdown(f"""
            <div style='font-size: 24px; font-family: "Segoe UI", sans-serif; color: #333; line-height: 1.6;'>
            {answer}
            </div>
            """, unsafe_allow_html=True)
