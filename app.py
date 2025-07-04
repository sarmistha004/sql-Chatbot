import streamlit as st
import mysql.connector
import openai
import os

# -------------------- CONFIG --------------------
st.set_page_config(page_title="DataWhiz - SQL Chatbot", layout="centered")

openai.api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# ✅ MySQL Connection
conn = mysql.connector.connect(
    host='sql12.freesqldatabase.com',
    port=3306,
    user='sql12787470',
    password='Tbsv7vtsVi',
    database='sql12787470'
)
cursor = conn.cursor()

# -------------------- LOGIN SYSTEM --------------------
users = {
    "Sarmistha Sen": "sarmistha@123",
    "Dr. Surajit Sen": "surajit@123",
    "Mithu Sen": "mithu@123"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to DataWhiz")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"✅ Welcome, {username}!")
            st.experimental_set_query_params(page="chatbot")  # Not necessary, optional
            st.toast("Loading Chatbot...", icon="💬")
        else:
            st.error("❌ Invalid credentials. Try again.")

# -------------------- MAIN CHATBOT --------------------
if st.session_state.logged_in:

    # ✅ Background & Styles
    st.markdown("""
        <style>
        body { background: linear-gradient(to right, #ffe6f0, #e6ccff); }
        header {visibility: hidden;}
        footer {visibility: hidden;}
        textarea {
            font-size: 18px !important;
            padding: 10px !important;
            min-height: 100px !important;
            font-family: 'Comic Sans MS', cursive;
        }
        .stButton > button {
            font-family: 'Comic Sans MS', cursive;
            font-size: 20px;
            background-color: #6C63FF;
            color: white;
            border-radius: 8px;
        }
        .stButton > button:hover {
            background-color: #483D8B;
            transform: scale(1.05);
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ App Title
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='font-size: 44px; color:#6C63FF; font-family:monospace;'>🤖 DataWhiz 💫</h1>
            <p style='font-size: 24px; color: deeppink; font-family: "Comic Sans MS", cursive; font-weight: bold;'>Your intelligent SQL assistant at your fingertips 🧠</p>
        </div>
    """, unsafe_allow_html=True)

    # ✅ Get Schema
    def get_schema(cursor):
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        schema = {}
        for (table_name,) in tables:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            schema[table_name] = [col[0] for col in columns]
        return schema

    # ✅ Generate SQL from GPT
    def generate_sql_query(user_question, schema_dict):
        schema_str = ""
        for table, cols in schema_dict.items():
            schema_str += f"Table {table} has columns: {', '.join(cols)}\n"
        prompt = f"""
        You are an expert SQL assistant. Based on the schema below, write a SQL query to answer the user's question.
        Use LOWER(TRIM(column)) LIKE LOWER('%value%') in WHERE clause.

        Schema:
        {schema_str}

        Question: {user_question}
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
                return "🤷 No data found."
            response = "<div style='font-size:24px; font-family: \"Comic Sans MS\", cursive;'>📊 Result:<br>"
            for row in results:
                response += " • " + ", ".join(str(i) for i in row) + "<br>"
            response += "</div>"
            return response
        except Exception as e:
            return f"<div style='font-size:24px; color:red;'>❌ SQL Error: {str(e)}</div>"

    # ✅ Chat UI
    sample_questions = [
        "None", "How many users are there?", "List all users above age 30",
        "Show names and emails of all users", "Show all users with name Sarmistha."
    ]
    st.selectbox("📜 Sample Questions", sample_questions, key="selected_question")
    user_question = st.text_area("💬 Ask your SQL question")

    search = st.button("🔍 Search")

    if search:
        q = user_question.strip() or st.session_state.selected_question
        if not q or q == "None":
            st.warning("⚠️ Ask a valid question.")
        elif q.lower() in ["hi", "hello"]:
            st.markdown("👋 Hello! How can I help you?")
        elif "thank" in q.lower():
            st.markdown("🙏 You're welcome! I'm here whenever you need me.")
        else:
            with st.spinner("⏳ Generating query..."):
                schema = get_schema(cursor)
                sql = generate_sql_query(q, schema)
                result = execute_sql_and_respond(sql)
                st.markdown(result, unsafe_allow_html=True)

    # ✅ Footer
    st.markdown("""
        <div style='
            position: fixed;
            bottom: 10px;
            left: 20px;
            background-color: #C71585;
            padding: 12px 20px;
            border-radius: 12px;
            box-shadow: 0 0 15px #C71585;
        '>
            <p style='font-size: 20px; color: white; font-family: "Comic Sans MS", cursive; margin: 0;'>Created By Sarmistha Sen</p>
        </div>
    """, unsafe_allow_html=True)

