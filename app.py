import streamlit as st
import mysql.connector
import openai
import os

# 🔐 Load OpenAI API key (use secrets or env variable)
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

        response = "📊 Result:\n"
        for row in results:
            response += " • " + ", ".join(str(i) for i in row) + "\n"
        return response.strip()

    except Exception as e:
        return f"❌ SQL Error: {str(e)}"

# ✅ Streamlit App UI
st.set_page_config(page_title="SQL Chatbot", layout="centered")

# 🧽 Hide header, footer, and top controls
hide_streamlit_ui = """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .css-15zrgzn {display: none;}
    </style>
"""
st.markdown(hide_streamlit_ui, unsafe_allow_html=True)

st.title("🧠 SQL Chatbot with OpenAI + MySQL")
st.markdown("Ask any question related to your database:")

# ✅ Input from user
user_question = st.text_input("💬 Enter your question:")

user_input = user_question.strip().lower()

if user_input == "":
    st.warning("⚠️ Please ask a valid question related to your database.")

elif user_input in ["hi", "hello", "hey"]:
    st.success("👋 Hi! How can I help you?")

elif "thank" in user_input:
    st.success("🙏 You're welcome! I'm always here to help you when you need.")

else:
    schema = get_schema(cursor)
    with st.spinner("⏳ Generating and executing SQL query..."):
        sql = generate_sql_query(user_question, schema)
        
        answer = execute_sql_and_respond(sql)
        st.markdown(answer)
