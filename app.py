import streamlit as st
import mysql.connector
import openai

# 🔐 Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 🛢️ Connect to MySQL
conn = mysql.connector.connect(
    host='sql12.freesqldatabase.com',
    port=3306,
    user='sql12787470',
    password='Tbsv7vtsVi',
    database='sql12787470'
)
cursor = conn.cursor()

# 📋 Get schema
def get_schema():
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    schema = {}
    for (table,) in tables:
        cursor.execute(f"DESCRIBE {table}")
        schema[table] = [col[0] for col in cursor.fetchall()]
    return schema

schema = get_schema()

# 🤖 Generate SQL using OpenAI
def generate_sql_query(question):
    schema_str = ""
    for table, cols in schema.items():
        schema_str += f"Table `{table}` has columns: {', '.join(cols)}\n"

    db_name = "sql12787470"

    prompt = f"""
You are an expert MySQL assistant for the `{db_name}` database.
Based on the schema provided below, write an accurate SQL query to answer the user's question.
ONLY return the SQL query — do NOT add explanations or natural language.

⚠️ VERY IMPORTANT:
- Always use this exact format for filtering strings:
  LOWER(TRIM(REPLACE(column, '\\r', ''))) = LOWER(TRIM(REPLACE('value', '\\r', '')))
- Do NOT use LIKE or %.
- Do NOT generate queries for greetings like "hi", "hello", "how are you", etc.

📊 SCHEMA:
{schema_str}

User question: {question}
SQL query:
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()

# 🔍 Run SQL and return result
def execute_sql_and_respond(question):
    sql_query = generate_sql_query(question)

    if not sql_query.lower().startswith("select"):
        return f"❌ Could not generate a valid SQL query. Please try rephrasing."

    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()

        if not results:
            return f"🔍 SQL: `{sql_query}`\n\n🤷 No data found."

        # Return friendly summary for COUNT/SUM/AVG
        if any(func in sql_query.lower() for func in ["count", "sum", "avg", "max", "min"]):
            return f"🔍 SQL: `{sql_query}`\n\n📊 Result: **{results[0][0]}**"

        # Default tabular response
        response = f"🔍 SQL: `{sql_query}`\n\n📊 Results:\n"
        for row in results:
            response += " • " + ", ".join(str(i) for i in row) + "\n"
        return response

    except Exception as e:
        return f"❌ Error running query:\n`{sql_query}`\n\n{e}"

# 🌐 Streamlit UI
st.set_page_config(page_title="SQL Chatbot", layout="centered")
st.title("🧠 SQL Chatbot with MySQL + OpenAI")

user_question = st.text_input("Ask a question about your database 👇")

# 💡 Greeting filter
greetings = ["hi", "hello", "hey", "how are you", "hii", "yo", "hlo", ""]

if user_question.lower().strip() in greetings:
    st.warning("⚠️ Please ask a valid question related to your database.")
elif user_question:
    st.markdown("💬 **Your Question:** " + user_question)
    with st.spinner("Generating SQL & fetching result..."):
        output = execute_sql_and_respond(user_question)
        st.markdown(output)
