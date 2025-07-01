import streamlit as st
import mysql.connector
from openai import OpenAI

# 💡 Streamlit UI setup
st.set_page_config(page_title="SQL Chatbot", layout="centered")
st.title("🧠 SQL Chatbot with MySQL + OpenAI")

# 🔐 Load OpenAI API key from secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🛢️ Connect to MySQL
conn = mysql.connector.connect(
    host='sql12.freesqldatabase.com',
    port=3306,
    user='sql12787470',
    password='Tbsv7vtsVi',
    database='sql12787470'
)
cursor = conn.cursor()

# 📋 Function to get schema
def get_schema():
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = {}
    for (table,) in tables:
        cursor.execute(f"DESCRIBE {table}")
        schema[table] = [col[0] for col in cursor.fetchall()]
    return schema

schema = get_schema()

# 📤 Function to show all table names
def display_tables():
    if not schema:
        return "❌ No tables found in the database."
    table_list = "📋 **Tables in your database:**\n"
    for t in schema:
        table_list += f"• `{t}` with columns: {', '.join(schema[t])}\n"
    return table_list

# 🧠 GPT: Generate SQL
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
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return None

# ⚙️ Execute query
def execute_sql_and_respond(question):
    sql_query = generate_sql_query(question)
    if not sql_query or "select" not in sql_query.lower():
        return "❗ I couldn't understand your question or generate a valid SQL. Try rephrasing it or asking something about the database."

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

# 🔎 User Interaction
user_question = st.text_input("Ask a question about your database 👇")

if user_question:
    if "show tables" in user_question.lower() or "list tables" in user_question.lower():
        st.markdown(display_tables())
    else:
        st.markdown("💬 **Your Question:** " + user_question)
        with st.spinner("Generating SQL & fetching result..."):
            output = execute_sql_and_respond(user_question)
            st.markdown(output)

