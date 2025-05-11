import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os
import pandas as pd
import paramiko
import io

from dashboard.anagrafica_dashboard import show_anagrafica_dashboard
from dashboard.anamnesi_dashboard import show_anamnesi_dashboard
from dashboard.consulenza_telematica_dashboard import show_consulenza_telematica_dashboard
from dashboard.contatto_telefonico_dashboard import show_contatto_telefonico_dashboard
from dashboard.coronarografia_ptca_dashboard import show_coronarografia_ptca_dashboard
from dashboard.dati_clinico_strumentali_ric_dashboard import show_dati_clinico_strumentali_ric_dashboard
from dashboard.ecocardio_dati_dashboard import show_ecocardio_dati_dashboard
from dashboard.ecocarotidi_dashboard import show_ecocarotidi_dashboard
from dashboard.esami_laboratorio_dashboard import show_esami_laboratorio_dashboard
from dashboard.esami_specialistici_dashboard import show_esami_specialistici_dashboard
from dashboard.esami_strumentali_cardio_dashboard import show_esami_strumentali_cardio_dashboard
from dashboard.lista_eventi_dashboard import show_lista_eventi_dashboard
from dashboard.ricovero_ospedaliero_dashboard import show_ricovero_ospedaliero_dashboard
from dashboard.visita_controllo_ecg_dashboard import show_visita_controllo_ecg_dashboard
from dashboard.visitacardiologica_dashboard import show_visitacardiologica_dashboard



# ——— Streamlit Config —————————————————————————————
st.set_page_config(page_title="Database Dashboard", layout="wide")
load_dotenv()

# ——— Connection Configuration ——————————————————————
DEFAULT_DB_CONFIG = {
    'host': os.getenv("MYSQL_HOST"),
    'port': int(os.getenv("MYSQL_PORT", 3306)),
    'database': os.getenv("MYSQL_DATABASE")
}

RPI_DATASET_DIR = "/home/rajib/Desktop/medical_dataset"  # CHANGE THIS TO YOUR RPI DATASET PATH

# ——— Session State Defaults —————————————————————————
if 'db_connected' not in st.session_state:
    st.session_state.update({
        'db_connected': False,
        'rpi_connected': False,
        'connection_type': None,
        'user': "",
        'password': "",
        'rpi_ip': "",
        'datasets': {},
        'selected_table': "None",
        'ssh_client': None,
        'rpi_username': "",
    })

# ——— Main —————————————————————————————————————
def main():
    if st.session_state.db_connected or st.session_state.rpi_connected:
        if st.session_state.connection_type == "Database":
            show_database_interface()
        else:
            show_raspberry_pi_interface()
    else:
        show_login_forms()

# ——— Combined Login Forms —————————————————————————
def show_login_forms():
    st.title("Connect to Data Source")
    col1, col2 = st.columns(2)
    with col1:
        show_database_login()
    with col2:
        show_raspberry_pi_login()

# ——— Database Login Form ——————————————————————————
def show_database_login():
    with st.expander("🔑 Database Login", expanded=True):
        with st.form("db_login"):
            st.markdown("Enter database credentials:")
            user = st.text_input("DB Username")
            password = st.text_input("DB Password", type="password")
            submitted = st.form_submit_button("Connect to Database")
            if submitted:
                handle_db_login(user, password)

# ——— Raspberry Pi Login Form ————————————————————————
def show_raspberry_pi_login():
    with st.expander("🖥️ Raspberry Pi Login", expanded=True):
        with st.form("rpi_login"):
            st.markdown("Enter Raspberry Pi credentials:")
            ip_address = st.text_input("RPi IP Address", placeholder="192.168.1.100")
            username = st.text_input("RPi Username", placeholder="pi")
            password = st.text_input("RPi Password", type="password")
            submitted = st.form_submit_button("Connect to Raspberry Pi")
            if submitted:
                handle_rpi_login(ip_address, username, password)

# ——— Database Login Handler ————————————————————————
def handle_db_login(user, password):
    if not user or not password:
        st.warning("Database credentials required")
        return

    try:
        with mysql.connector.connect(**DEFAULT_DB_CONFIG, user=user, password=password) as conn:
            conn.ping(reconnect=True, attempts=3)
        st.session_state.db_connected = True
        st.session_state.connection_type = "Database"
        st.session_state.user = user
        st.session_state.password = password
        st.toast("Database connected!", icon="✅")
        load_datasets()
    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")

# ——— Raspberry Pi Login Handler ——————————————————————
def handle_rpi_login(ip, username, password, debug=False):
    if not validate_ip(ip):
        st.error("Invalid IP address format")
        return

    if st.session_state.get('ssh_client'):
        st.session_state.ssh_client.close()
        st.session_state.ssh_client = None

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ip, username=username, password=password, timeout=10, look_for_keys=False, allow_agent=False)
        ssh.get_transport().set_keepalive(60)

        stdin, stdout, stderr = ssh.exec_command(f"ls {RPI_DATASET_DIR}")
        if stderr.read():
            raise Exception("Dataset directory not found or permission denied")

        st.session_state.ssh_client = ssh
        st.session_state.rpi_connected = True
        st.session_state.connection_type = "Raspberry Pi"
        st.session_state.rpi_ip = ip
        st.session_state.rpi_username = username
        st.session_state.password = password
        st.toast("RPi connected!", icon="✅")

        load_rpi_datasets_ssh(ssh, RPI_DATASET_DIR, debug)
    except paramiko.AuthenticationException:
        st.error("Authentication failed: Invalid username/password")
    except paramiko.SSHException as e:
        st.error(f"SSH error: {e}")
    except Exception as e:
        st.error(f"Connection failed: {e}")

# ——— Database Interface ———————————————————————————
def show_database_interface():
    st.title("📊 Database Explorer")
    if not st.session_state.datasets:
        st.warning("No datasets found")
        return

    st.sidebar.title("📂 Available Datasets")
    options = ["None"] + list(st.session_state.datasets.keys())
    selected_table = st.sidebar.radio("Select Dataset", options)
    st.session_state.selected_table = selected_table

    display_dataset_content()

    if st.button("Disconnect"):
        handle_disconnect()

# ——— Raspberry Pi Interface —————————————————————————
def show_raspberry_pi_interface():
    st.title("📊 Raspberry Pi Database Explorer")
    if not st.session_state.datasets:
        st.warning("No datasets found on Raspberry Pi")
        return

    st.sidebar.title("📂 Available Datasets")
    options = ["None"] + list(st.session_state.datasets.keys())
    selected_table = st.sidebar.radio("Select Dataset", options)
    st.session_state.selected_table = selected_table

    display_dataset_content()

    if st.button("Disconnect"):
        handle_disconnect()

# ——— Shared Dataset Display —————————————————————————
def display_dataset_content():
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
        elif sel == "contatto_telefonico":
            show_contatto_telefonico_dashboard(df)
        elif sel == "coronarografia_ptca":
            show_coronarografia_ptca_dashboard(df)
        elif sel == "dati_clinico_strumentali_ric":
            show_dati_clinico_strumentali_ric_dashboard(df)
        elif sel == "ecocardio_dati":
            show_ecocardio_dati_dashboard(df)
        elif sel == "ecocarotidi":
            show_ecocarotidi_dashboard(df)
        elif sel == "esami_laboratorio":
            show_esami_laboratorio_dashboard(df)
        elif sel == "esami_specialistici":
            show_esami_specialistici_dashboard(df)
        elif sel == "esami_strumentali_cardio":
            show_esami_strumentali_cardio_dashboard(df)
        elif sel == "lista_eventi":
            show_lista_eventi_dashboard(df)
        elif sel == "ricovero_ospedaliero":
            show_ricovero_ospedaliero_dashboard(df)
        elif sel == "visita_controllo_ecg":
            show_visita_controllo_ecg_dashboard(df)
        elif sel == "visitacardiologica":
            show_visitacardiologica_dashboard(df)
        else:
            display_table_preview(sel)

# ——— Load MySQL Datasets —————————————————————————
def load_datasets():
    with st.spinner("Loading database tables..."):
        conn = mysql.connector.connect(**DEFAULT_DB_CONFIG,
                                       user=st.session_state.user,
                                       password=st.session_state.password)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        datasets = {}
        for (table,) in cursor.fetchall():
            cursor.execute(f"SELECT * FROM `{table}`;")
            rows = cursor.fetchall()
            cols = [d[0] for d in cursor.description]
            datasets[table] = pd.DataFrame(rows, columns=cols)
        cursor.close()
        conn.close()
        st.session_state.datasets = datasets

# ——— Load RPi Datasets ——————————————————————————
def load_rpi_datasets_ssh(ssh, dataset_dir, debug=False):
    with st.spinner("Reading CSV datasets from Raspberry Pi..."):
        try:
            cmd = f"ls {dataset_dir}/*.csv"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            file_list = stdout.read().decode().splitlines()
            if not file_list:
                st.warning("No CSV files found.")
                return

            datasets = {}
            for file_path in file_list:
                filename = os.path.basename(file_path)
                name = os.path.splitext(filename)[0].lower()
                read_cmd = f"head -n 500 {file_path}"
                #read_cmd = f"cat {file_path}"
                stdin, stdout, stderr = ssh.exec_command(read_cmd)
                csv_content = stdout.read().decode()
                df = pd.read_csv(io.StringIO(csv_content))
                datasets[name] = df

            st.session_state.datasets = datasets
        except Exception as e:
            st.error(f"Dataset read error: {e}")
            if debug:
                st.session_state.debug_log.append(str(e))

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

# ——— Disconnect Handler ——————————————————————————
def handle_disconnect():
    keys_to_clear = [
        'db_connected', 'rpi_connected', 'connection_type',
        'user', 'password', 'rpi_ip', 'datasets', 'selected_table'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ——— Helper Functions ———————————————————————————
def validate_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(
        part.isdigit() and 0 <= int(part) <= 255 
        for part in parts
    )

if __name__ == "__main__":
    main()
