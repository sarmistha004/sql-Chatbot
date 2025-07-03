import streamlit as st
import mysql.connector
import openai
import os

# 🔐 Load OpenAI API key
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
instead of = or plain LIKE.

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

        response = "<div style='font-size:24px;'>📊 Result:<br>"
        for row in results:
            response += " • " + ", ".join(str(i) for i in row) + "<br>"
        response += "</div>"
        return response

    except Exception as e:
        return f"<div style='font-size:24px; color:red;'>❌ SQL Error: {str(e)}</div>"

# ✅ Streamlit App UI
st.set_page_config(page_title="DataWhiz - SQL Chatbot", layout="centered")

# 🧽 Hide Streamlit header, footer, and menu
hide_streamlit_ui = """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .css-15zrgzn {display: none;}
    textarea {
        font-size: 18px !important;
        padding: 10px !important;
        min-height: 100px !important;
    }
    </style>
"""
st.markdown(hide_streamlit_ui, unsafe_allow_html=True)

# ✅ Centered Stylish Title with Tagline
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='font-size: 44px; color:#6C63FF; font-family:monospace;'>🤖 DataWhiz 💫</h1>
        <p style='font-size: 24px; color: #FF8C00; font-weight: bold;'>Your intelligent SQL assistant at your fingertips 🧠</p>
        <p style='font-size: 22px; font-weight: bold;'>Ask anything about your MySQL database below:</p>
    </div>
    <br>
    <p style='font-size: 22px; font-weight: bold;'>💬 <b>Enter your question:</b></p>
""", unsafe_allow_html=True)


# ✅ Dropdown for sample questions
sample_questions = [
    "None",
    "How many users are there?",
    "List all users above age 30",
    "Show names and emails of all users",
    "What is the average age of users?",
    "Show all users registered in June",
    "Show all users with name Sarmistha."
]

st.markdown("<p style='font-size:20px;'>📜 <b>Select a sample question or type your own:</b></p>", unsafe_allow_html=True)

selected_question = st.selectbox("Choose a question", sample_questions)

# ✅ Text input for custom questions
user_question = st.text_area(
    label="Ask a SQL-related question",
    label_visibility="collapsed",
    height=120,
    placeholder="Or type your own SQL-related question here...",
    key="user_input_box"
)

# If user types something, it overrides the selected one
displayed_question = user_question if user_question.strip() else selected_question

# ✅ Search Button
search = st.button("🔍 Search")

# ✅ Input Processing
if search:
    user_input = displayed_question.strip().lower()

    if user_input == "":
        st.warning("⚠️ Please ask a valid question related to your database.")

    elif user_input in ["hi", "hello", "hey"]:
        st.markdown("<p style='font-size:24px; color:green;'>👋 <b>Hello!</b> How can I help you?</p>", unsafe_allow_html=True)

    elif "thank" in user_input:
        st.markdown("<p style='font-size:24px; color:#2E8B57;'>🙏 You're welcome! I'm always here to help you when you need.</p>", unsafe_allow_html=True)

    else:
        schema = get_schema(cursor)
        with st.spinner("⏳ Generating and executing SQL query..."):
            sql = generate_sql_query(displayed_question, schema)
            answer = execute_sql_and_respond(sql)
            st.markdown(answer, unsafe_allow_html=True)

