# 🏥 Medical Database Dashboard

A sleek and intuitive **dashboard interface** built to access and manage medical datasets. It supports seamless connectivity to either a **Dockerized MySQL server** or a **Raspberry Pi-based database server**, giving you flexibility in deployment.

🔗 [👉 View the Live Dashboard Here 👈](https://medicaldatabasedashboard-kvpsm4xuptbxabjcxtvgdw.streamlit.app/)

---

## 🚀 Getting Started

You can choose between two backend connection options:

### 🔹 Option 1: Docker MySQL Server

Quick and containerized setup using Docker.

#### 1. Pull the Docker Image

Run this command to download the pre-configured image:

```bash
    Start the Docker 
    docker pull example:v1
    Run the docker image with this command: docker run -d -p 3306:3306 --name example examplel:v1
```

#### 1. Connect via MySQL Server

#### Make sure your Docker Container is running and connect to the Docker MySQL server, Provide the following information in the MySQL Credential:

```bash
    Username: your_mysql_username
    Password: your_mysql_password
```

### 🔹 Option 2: Connect via Raspberry Pi Server

#### If you prefer to use a Raspberry Pi server instead of Docker:

Make sure your Raspberry Pi server is running and the database service is accessible. Provide the following information in the Raspberry Pi Credential:

```bash
    IP Address: raspberry_pi_ip
    Username: raspberry_pi_username
    Password: raspberry_pi_password
```

Ensure the necessary ports are open and the server allows remote connections.

## 📊 About the Dashboard

The dashboard enables users to:

- 🔹 Connect to a medical database
- 🔁 Switch between Docker MySQL or Raspberry Pi backends
- 📊 Visualize and interact with medical datasets
