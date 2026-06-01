# 🌐 ZeroClick Hosting Guide

This guide will help you deploy ZeroClick to various platforms using the provided Docker setup.

## 🚀 Option 1: Railway.app (Recommended)

1.  **Fork/Push** this repository to your GitHub.
2.  Log in to [Railway.app](https://railway.app/).
3.  Click **New Project** > **Deploy from GitHub repo**.
4.  Select your `ZeroClick` repository.
5.  Railway will detect the `Dockerfile` automatically.
6.  **Important:** Go to **Variables** and add:
    *   `PORT`: `8000`
7.  Go to **Settings** > **Networking** and click **Generate Domain**.

---

## ☁️ Option 2: VPS (DigitalOcean / Hetzner)

If you are using a standard Ubuntu VPS:

1.  **Install Docker:**
    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    ```
2.  **Clone your repo:**
    ```bash
    git clone https://github.com/yourusername/ZeroClick.git
    cd ZeroClick
    ```
3.  **Build and Run:**
    ```bash
    docker build -t zeroclick .
    docker run -d -p 80:8000 --name zeroclick-app -e PORT=8000 zeroclick
    ```

---

## 🏠 Option 3: Local Home Server (Cloudflare Tunnel)

If you want to host it from your Windows/Linux PC at home:

1.  Run the app locally or via Docker.
2.  Download `cloudflared` from [Cloudflare](https://github.com/cloudflare/cloudflared/releases).
3.  Run:
    ```bash
    cloudflared tunnel --url http://localhost:8000
    ```
4.  Cloudflare will give you a temporary URL like `https://random-words.trycloudflare.com`.

---

## 🛠️ Maintenance & Registry

*   **Registry:** To add new apps, edit `data/apps.json` and restart the container, OR use the `/add-app` API endpoint.
*   **Persistent Data:** Ensure the `data/` folder is backed up. If using Docker, you should use a volume:
    ```bash
    docker run -v $(pwd)/data:/app/data ...
    ```
*   **Stub file:** Make sure `data/stub.exe` exists before deploying if you want to use the **Installer Generator** feature.
