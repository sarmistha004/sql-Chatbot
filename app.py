import streamlit as st
import mysql.connector
from openai import OpenAI
import os

# 🌟 Set up OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 📦 Connect to MySQL database
conn = mysql.connector.connect(
    host='sql12.freesqldatabase.com',
    port=3306,
    user='sql12787470',
    password='Tbsv7vtsVi',
    database='sql12787470'
)
cursor = conn.cursor()

# 📄 Get schema of all tables
def get_schema():
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = {}
    for (table,) in tables:
        cursor.execute(f"DESCRIBE {table}")
        schema[table] = [col[0] for col in cursor.fetchall()]
    return schema

schema = get_schema()

# 🧠 GPT-powered SQL generator
def generate_sql_query(question):
    schema_str = ""
    for table, cols in schema.items():
        schema_str += f"Table `{table}` has columns: {', '.join(cols)}\n"

    prompt = f"""
You are an expert SQL assistant. Based on the schema below, write a SQL query to answer the user's question.
Only return the SQL query without explanation.

{schema_str}

User question: {question}
SQL query:
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# 🚦 Handle vague inputs and run GPT + SQL
def execute_sql_and_respond(question):
    VAGUE_INPUTS = {"hello", "hi", "hey", "thanks", "thank you", "bye", "how are you"}

    q_clean = question.lower().strip()
    if q_clean in VAGUE_INPUTS:
        return "👋 Hi! I'm your SQL assistant. Ask something like:\n\n• How many users are registered?\n• What are the emails of users under 30?"

    if q_clean in {"show tables", "show schema"}:
        schema_lines = [f"🔹 `{table}` → {', '.join(cols)}" for table, cols in schema.items()]
        return "📋 **Database Schema:**\n\n" + "\n".join(schema_lines)

    # Normal SQL query flow
    sql_query = generate_sql_query(question)
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if not results:
            return f"🔍 SQL: `{sql_query}`\n\n🤷 No data found."
        response = f"🔍 SQL: `{sql_query}`\n\n📊 Result:\n"
        for row in results:
            response += " • " + ", ".join(str(i) for i in row) + "\n"
        return response
    except Exception as e:
        return f"❌ Error running query:\n`{sql_query}`\n\n{e}"

# 🌐 Streamlit UI setup
st.set_page_config(page_title="SQL Chatbot", layout="centered")
st.title("🧠 SQL Chatbot with MySQL + OpenAI")

user_question = st.text_input("Ask a question about your database 👇")

if user_question:
    st.markdown("💬 **Your Question:** " + user_question)
    with st.spinner("Generating SQL & fetching result..."):
        output = execute_sql_and_respond(user_question)
        st.markdown(output)

