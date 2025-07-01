import streamlit as st
import mysql.connector
import openai
import os

# 🔐 Load API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host='sql12.freesqldatabase.com',
    port=3306,
    user='sql12787470',
    password='Tbsv7vtsVi',
    database='sql12787470'
)
cursor = conn.cursor()

# ✅ Get Schema
def get_schema():
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = {}
    for (table,) in tables:
        cursor.execute(f"DESCRIBE {table}")
        schema[table] = [col[0] for col in cursor.fetchall()]
    return schema

schema = get_schema()

# ✅ Generate SQL with OpenAI
def generate_sql_query(question):
    schema_str = ""
    for table, cols in schema.items():
        schema_str += f"Table {table} has columns: {', '.join(cols)}\n"

    prompt = f"""
You are an expert SQL assistant. Based on the schema below, write a SQL query to answer the user's question.
Only return the SQL query without explanation.

Use strict string match for name comparisons using:
LOWER(TRIM(column)) = LOWER('value')

Avoid LIKE and fuzzy matches.

{schema_str}

User question: {question}
SQL query:
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().strip("`")

# ✅ Execute SQL
def execute_sql_and_respond(sql_query):
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()

        if not results:
            return "🤷 No data found for your query."

        # If aggregate, return clean
        if any(kw in sql_query.lower() for kw in ["count", "avg", "sum", "min", "max"]):
            return f"📊 Answer: **{results[0][0]}**"

        # Return rows
        response = "📊 Results:\n"
        for row in results:
            response += " • " + ", ".join(str(i) for i in row) + "\n"
        return response.strip()

    except Exception as e:
        return f"❌ SQL Error:\n{e}"

# ✅ Wipe all data (truncate)
def clear_all_data():
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for (table,) in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        return "🧹 All data deleted from your database!"
    except Exception as e:
        return f"❌ Error deleting data:\n{e}"

# ✅ Streamlit App UI
st.set_page_config(page_title="SQL Chatbot", layout="centered")
st.title("🧠 SQL Chatbot with MySQL + OpenAI")
st.markdown("Ask questions about your database in natural language!")

# 🔘 Optional: Clear DB
if st.button("🧹 Clear All Table Data"):
    msg = clear_all_data()
    st.success(msg)

# 💬 Ask a question
user_question = st.text_input("💬 Your Question")

# 🚀 Process
if user_question:
    with st.spinner("Generating SQL and fetching results..."):
        sql_query = generate_sql_query(user_question)
        st.code(sql_query, language="sql")
        response = execute_sql_and_respond(sql_query)
        st.markdown(response)

