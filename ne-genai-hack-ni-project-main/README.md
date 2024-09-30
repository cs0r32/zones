# Deployment Guide

> on render.com

- Build Command - `mkdir .streamlit; cp /etc/secrets/secrets.toml ./.streamlit/; pip install -r requirements.txt`
- Start Command - `streamlit run main.py`

## Environment

- client_secret.json - from Google OAuth credentials console
- secrets.toml
- Env Variables

```bash
PYTHON_VERSION=3.11.5
```
