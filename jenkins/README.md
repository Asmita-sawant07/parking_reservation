# Local Jenkins Setup Guide

This guide explains how to run a local Jenkins CI server using Docker on macOS for the **Parking Reservation System** pipeline.

---

## 📋 Prerequisites

- **Docker Desktop for Mac** must be installed and running.
- Port **8080** available on your machine (to access the Jenkins web dashboard).

---

## 🚀 1. Run Jenkins Using Docker

To start Jenkins as a background container, run the following command in your macOS terminal:

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

### Explanation of Command Flags:
- `-d`: Runs the container in the background (detached mode).
- `--name jenkins`: Assigns an easy-to-use name to the container.
- `-p 8080:8080`: Maps port `8080` of your Mac to port `8080` of Jenkins (Web UI).
- `-p 50000:50000`: Exposes the Jenkins agent communication port.
- `-v jenkins_home:/var/jenkins_home`: Persists Jenkins configuration, jobs, and plugins in a named Docker volume so your work is not lost when the container stops.
- `jenkins/jenkins:lts`: Official Jenkins Long-Term Support (LTS) image (fully compatible with Apple Silicon).

---

## 🔑 2. How to Retrieve the Initial Admin Password

When Jenkins starts for the first time, it generates a secure temporary admin password.

### Option A: Read the password file directly (Fastest)
Run this single command in your terminal:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Option B: View container logs
```bash
docker logs jenkins
```
Look for the password block printed between asterisks, for example:
```text
*************************************************************
*************************************************************
*************************************************************

Jenkins initial setup is required. An admin user has been created and a password generated.
Please use the following password to proceed to installation:

4a2b6c8d1e3f...  <-- Copy this 32-character password

This may also be found at: /var/jenkins_home/secrets/initialAdminPassword
*************************************************************
```

---

## 🌐 3. First-Time Setup in the Browser

1. Open your web browser and navigate to:
   ```text
   http://localhost:8080
   ```
2. Paste the **initial admin password** copied in Step 2 and click **Continue**.
3. On the *Customize Jenkins* page, click **Install suggested plugins** (this installs Git, Pipeline, and essential plugins automatically).
4. Wait for the plugin installations to complete.
5. Create your **First Admin User** (enter username, password, full name, and email) and click **Save and Continue**.
6. On the *Instance Configuration* screen, keep the default URL (`http://localhost:8080/`) and click **Save and Finish**.
7. Click **Start using Jenkins**.

---

## 🔄 4. Managing the Jenkins Container

- **Check if Jenkins is running:**
  ```bash
  docker ps
  ```
- **Stop Jenkins:**
  ```bash
  docker stop jenkins
  ```
- **Restart Jenkins later:**
  ```bash
  docker start jenkins
  ```
- **Remove the container (preserves your data in the `jenkins_home` volume):**
  ```bash
  docker rm jenkins
  ```
- **Completely clean up Jenkins and all saved data:**
  ```bash
  docker rm -f jenkins
  docker volume rm jenkins_home
  ```
