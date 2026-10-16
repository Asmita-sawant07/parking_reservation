# Local Jenkins Setup Guide

This guide explains how to build and run a custom Jenkins CI/CD container on macOS (Apple Silicon compatible) for the **Parking Reservation System** pipeline.

The custom image includes **Python 3**, **python3-venv**, **python3-pip**, and the **Docker CLI** so that Jenkins pipelines can create virtual environments, execute `pytest`, and build Docker containers.

---

## 📋 Prerequisites

- **Docker Desktop for Mac** must be installed and running.
- Port **8080** available on your machine (to access the Jenkins web dashboard).

---

## 🏗️ 1. Build the Custom Jenkins Image

From the root of your `parking_reservation` project, run:

```bash
docker build -t custom-jenkins:latest jenkins/
```

This builds the image defined in `jenkins/Dockerfile` with Python 3, venv, pip, and Docker CLI pre-installed.

---

## 🚀 2. Run the Custom Jenkins Container

Start the custom Jenkins container with port 8080, persistent storage, and the Docker daemon socket mounted:

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  custom-jenkins:latest
```

### Explanation of Command Flags:
- `-d`: Runs the container in the background (detached mode).
- `--name jenkins`: Assigns an easy-to-use container name.
- `-p 8080:8080`: Maps port `8080` of your Mac to port `8080` of Jenkins (Web UI).
- `-p 50000:50000`: Port for Jenkins agent communication.
- `-v jenkins_home:/var/jenkins_home`: Persists Jenkins configuration, jobs, and plugins in a named Docker volume across container restarts.
- `-v /var/run/docker.sock:/var/run/docker.sock`: Mounts the host Docker daemon socket so the Jenkins container's Docker CLI can interact with Docker Desktop to build, scan, and run container images.
- `custom-jenkins:latest`: Uses the image built from `jenkins/Dockerfile`.

---

## 🔑 3. How to Retrieve the Initial Admin Password

When Jenkins starts for the first time, it generates a secure temporary admin password.

### Option A: Read the password file directly (Fastest)
Run this command in your terminal:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Option B: View container logs
```bash
docker logs jenkins
```
Look for the 32-character alphanumeric password printed between lines of asterisks (`****`).

---

## 🌐 4. First-Time Setup in the Browser

1. Open your browser and navigate to:
   ```text
   http://localhost:8080
   ```
2. Paste the **initial admin password** copied in Step 3 and click **Continue**.
3. On the *Customize Jenkins* page, click **Install suggested plugins** (this installs Git, Pipeline, and essential plugins automatically).
4. Wait for the plugin installations to complete.
5. Create your **First Admin User** (enter username, password, full name, and email) and click **Save and Continue**.
6. On the *Instance Configuration* screen, keep the default URL (`http://localhost:8080/`) and click **Save and Finish**.
7. Click **Start using Jenkins**.

---

## 🔄 5. Managing the Jenkins Container

- **Check container status:**
  ```bash
  docker ps
  ```
- **View live Jenkins logs:**
  ```bash
  docker logs -f jenkins
  ```
- **Stop Jenkins:**
  ```bash
  docker stop jenkins
  ```
- **Restart Jenkins later:**
  ```bash
  docker start jenkins
  ```
- **Remove the container (preserves pipeline data in `jenkins_home` volume):**
  ```bash
  docker rm jenkins
  ```
- **Completely reset Jenkins and remove saved volume data:**
  ```bash
  docker rm -f jenkins
  docker volume rm jenkins_home
  ```
