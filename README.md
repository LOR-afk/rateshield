# RateShield

A small API security lab for experimenting with request rate limiting, suspicious login detection, and IP-based risk scoring.

Built with **FastAPI**, **React/Vite**, and **MySQL/MariaDB**. The application includes a configurable sliding-window request limiter, simulated authentication events, a security event log, and a monitoring dashboard.

## What it does

- Enforces a configurable per-IP limit on `/api/protected/ping`, returning HTTP 429 and `Retry-After` when exceeded
- Tracks simulated failed login attempts and flags repeated failures
- Assigns a simple risk score based on blocked requests and failed logins
- Saves event metadata to MySQL/MariaDB and displays recent activity in React
- Lets you adjust local test policies from the dashboard

## Run locally (Windows + XAMPP, no Docker)

1. Start **MySQL** in XAMPP, and Apache if you want phpMyAdmin.
2. Create a database called `rateshield` in phpMyAdmin.
3. Copy `backend/.env.example` to `backend/.env`. Default XAMPP root-without-password works with the example connection string. Adjust credentials/port as needed.
4. Run the backend from the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

5. Open a **second terminal**:

```powershell
cd frontend
npm install
npm run dev
```

React: http://127.0.0.1:5173  
FastAPI docs: http://127.0.0.1:8000/docs  
API health: http://127.0.0.1:8000/api/health

## Test it

Open the dashboard and click **Send 12 requests**. The default policy allows 10 requests per 60 seconds, so 2 should be blocked with HTTP 429. Click **Simulate failed logins** to generate four dummy failures and a suspicious-login signal.

From `backend/`, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Project structure

```text
rateshield/
├── backend/
│   ├── app/
│   ├── migrations/versions/
│   ├── tests/
│   ├── schema.sql
│   ├── seed.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── erd.md
│   └── openapi.yaml
└── README.md
```

## Technical notes

This MVP uses an **in-memory sliding-window limiter**, shared by requests in a single Python process. Counters reset on restart and are **not shared between workers**. Database events persist after restart. Redis or another centralized counter store is needed before a multi-worker deployment.

The risk score is a simple heuristic (`25 × blocked requests + 15 × failed logins`, capped at 100) calculated from the latest 1,000 events; it is **not** a validated threat intelligence score. It can grow over time and should not be interpreted as a calibrated probability.

IP is obtained from the direct connection, not blindly from `X-Forwarded-For`. Behind a reverse proxy, additional trusted-proxy configuration would be needed. Localhost demo tools are disabled unless `DEMO_MODE=true` and the request comes from a loopback address.

**Do not expose this API/dashboard to the public internet.** There is no authentication for the administrative dashboard. Use only your own development traffic. The application stores IP addresses and event metadata, so apply appropriate retention and access controls before real-world use.

## Author

Lore Lindell Tamayo — [GitHub](https://github.com/LOR-afk)
