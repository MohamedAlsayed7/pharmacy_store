# Pharmacy Store — Khaleek Qawi (Demo)

This project contains two parts:
- `frontend/` — static HTML/CSS/JS store (can be hosted on GitHub Pages or served locally).
- `backend/` — Flask app to receive orders and store them in SQLite, and a simple admin panel protected by HTTP Basic Auth.

## Quick start (local)

1. Unzip the project and open a terminal.
2. Frontend-only (no backend required) — open `frontend/index.html` in your browser (or serve with a static server).

3. To run backend (recommended for storing orders):
   - Create virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate   # Windows: venv\Scripts\activate
     ```
   - Install requirements:
     ```bash
     pip install -r backend/requirements.txt
     ```
   - Set admin password (optional) via environment variable `ADMIN_PASSWORD`. If not set, default is `admin123`.
   - Run backend:
     ```bash
     python backend/app.py
     ```
   - Open the store at: http://localhost:5000
   - Admin panel: http://localhost:5000/backend/admin  (username: admin, password: ADMIN_PASSWORD or admin123)

## WhatsApp orders
- The "Send via WhatsApp" button opens WhatsApp web or app with a prefilled message to your number (international format is used in the frontend JS).

## Notes & Disclaimer
- This is a demo/educational project. Selling medicines online requires regulatory compliance and licensing — this project is NOT a production-ready pharmacy.
- Images used are public-domain Wikimedia Commons images or generic placeholders for demo purposes.
