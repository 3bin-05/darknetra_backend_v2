# DarkNetra Backend

FastAPI-based backend for the DarkNetra phishing URL detection application.

## Local Development

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment and install dependencies:
   ```bash
   # Windows:
   .venv\Scripts\pip install -r requirements.txt
   
   # Linux/Mac:
   .venv/bin/pip install -r requirements.txt
   ```
3. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

---

## Render Free-Tier Keep-Alive

To prevent the Render free-tier web service from spinning down due to inactivity, this repository includes a GitHub Actions keep-alive workflow.

### Setup Instructions

1. **Get your deployed Render App URL** (e.g., `https://darknetra-backend.onrender.com`).
2. **Add a Repository Secret** on GitHub:
   - Go to your repository on GitHub.
   - Navigate to **Settings** → **Secrets and variables** → **Actions**.
   - Click **New repository secret**.
   - **Name**: `RENDER_APP_URL`
   - **Value**: Your deployed Render application URL (e.g., `https://darknetra-backend.onrender.com` — *do not include a trailing slash*).
3. The workflow runs automatically every 10 minutes to ping the `/health` endpoint and keep the server active.

> [!NOTE]
> This is a best-effort keep-alive. Occasional cold starts are still possible if GitHub's scheduler experiences delays.