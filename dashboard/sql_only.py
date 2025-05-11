import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

from pages.dashboard.anagrafica_dashboard import show_anagrafica_dashboard
from pages.dashboard.anamnesi_dashboard   import show_anamnesi_dashboard
from pages.dashboard.consulenza_telematica_dashboard import show_consulenza_telematica_dashboard

# ——— Streamlit Config —————————————————————————————
st.set_page_config(page_title="Database Dashboard", layout="centered")
load_dotenv()



DEFAULT_CONFIG = {
    'host':     os.getenv("MYSQL_HOST"),
    'port':     int(os.getenv("MYSQL_PORT", 3306)),
    'database': os.getenv("MYSQL_DATABASE")
}

# ——— Session State Defaults —————————————————————————
if 'connected' not in st.session_state:
    st.session_state.connected       = False
    st.session_state.user            = ""
    st.session_state.password        = ""
    st.session_state.datasets        = {}
    # Initialize selected_table to "None"
    st.session_state.selected_table  = "None"

# ——— Main —————————————————————————————————————
def main():
    if not st.session_state.connected:
        show_login_form()
    else:
        show_database_interface()

# ——— Login Form —————————————————————————————————
def show_login_form():
    #st.markdown("## 🔑 Database Connection", unsafe_allow_html=True)
    st.title("🔑 Database Connection")
    with st.expander("Initialize the SQL connection", expanded=True):
        st.markdown("Please enter your credentials to connect to the database.")
        with st.form("login"):
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Connect")
            if submitted:
                handle_login(user, password)

# ——— Handle Login —————————————————————————————
def handle_login(user, password):
    if not user or not password:
        st.warning("Both username and password are required.")
        return

    try:
        with mysql.connector.connect(**DEFAULT_CONFIG, user=user, password=password) as conn:
            conn.ping(reconnect=True, attempts=3)
        st.session_state.connected = True
        st.session_state.user      = user
        st.session_state.password  = password
        st.toast("🔗 Connected!", icon="✅")
        

    except mysql.connector.Error as e:
        st.error(f"Connection failed: {e}")

# ——— Main Interface —————————————————————————————
def show_database_interface():
    st.title("📊 Database Explorer")

    # Ensure datasets loaded once
    if not st.session_state.datasets:
        load_datasets()

    # Sidebar selector (no index=, simple key)
    st.sidebar.title("📂 Available Datasets")
    options = ["None"] + list(st.session_state.datasets.keys())
    st.sidebar.radio("Select Dataset", options, key="selected_table")

    sel = st.session_state.selected_table

    if sel == "None":
        display_overview()
    else:
        df = st.session_state.datasets[sel]
        if sel == "anagrafica":
            show_anagrafica_dashboard(df)
        elif sel == "anamnesi":
            show_anamnesi_dashboard(df)
        elif sel == "consulenza_telematica":
            show_consulenza_telematica_dashboard(df)
        else:
            display_table_preview(sel)

    if st.button("Disconnect"):
        handle_disconnect()

# ——— Load all tables ————————————————————————————
def load_datasets():
    with st.spinner("Loading tables..."):
        conn = mysql.connector.connect(**DEFAULT_CONFIG,
                                       user=st.session_state.user,
                                       password=st.session_state.password)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        for (table,) in cursor.fetchall():
            cursor.execute(f"SELECT * FROM `{table}`;")
            rows  = cursor.fetchall()
            cols  = [d[0] for d in cursor.description]
            df    = pd.DataFrame(rows, columns=cols)
            st.session_state.datasets[table] = df
        cursor.close()
        conn.close()

# ——— Overview for None ——————————————————————————
def display_overview():
    st.subheader("📋 Dataset Overview")
    st.info("Select a dataset from the sidebar to view its dashboard.")
    for name, df in st.session_state.datasets.items():
        st.markdown(f"**{name}**: {df.shape[0]} rows × {df.shape[1]} cols")
        st.dataframe(df.head(100), use_container_width=True)
        st.divider()

# ——— Generic Preview ————————————————————————————
def display_table_preview(table_name):
    st.subheader(f"🔍 Preview: `{table_name}`")
    df = st.session_state.datasets[table_name]
    st.dataframe(df.head(100), use_container_width=True)
    with st.expander("Statistics"):
        st.write(df.describe(include='all'))

# ——— Disconnect ——————————————————————————————
def handle_disconnect():
    for key in ['connected','user','password','datasets','selected_table']:
        if key in st.session_state:
            del st.session_state[key]
    #st.experimental_rerun()
    # Explicitly set current view to home
        #st.switch_page("App/home.py")
        st.rerun()
        

# ——— Run —————————————————————————————————————
if __name__ == "__main__":
    main()
