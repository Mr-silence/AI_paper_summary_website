# Ubuntu Production Deployment

This project is deployed as a single-host Ubuntu stack:

- `nginx` serves `frontend/dist`
- `uvicorn` serves FastAPI on `127.0.0.1:8000`
- `mysql-server` stores application data
- `cron` runs the daily update and digest jobs

## Target layout

```text
/srv/ai-paper-summary/
├── backend/
│   ├── .env
│   ├── runtime/logs/
│   └── venv/
└── frontend/
    └── dist/
```

## 1. Install system dependencies

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-venv mysql-server nginx curl
```

Install Node.js 20 LTS:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 2. Clone or update the repository

```bash
sudo mkdir -p /srv
sudo chown ubuntu:ubuntu /srv
cd /srv
git clone https://github.com/Mr-silence/AI_paper_summary_website.git ai-paper-summary
cd /srv/ai-paper-summary
```

If the repo already exists:

```bash
cd /srv/ai-paper-summary
git pull origin main
```

## 3. Configure the backend

```bash
cd /srv/ai-paper-summary/backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
mkdir -p runtime/logs
```

Edit `backend/.env` with the production values:

- `DATABASE_URL=mysql+pymysql://ai_paper_summary:<strong-password>@localhost:3306/ai_paper_summary`
- `MYSQL_UNIX_SOCKET=`
- `BACKEND_PUBLIC_URL=http://43.155.154.193`
- `FRONTEND_URL=http://43.155.154.193`
- `KIMI_API_KEY=<your-kimi-api-key>`
- `SMTP_HOST=smtp.gmail.com`
- `SMTP_PORT=587`
- `SMTP_USERNAME=z1332556430@gmail.com`
- `SMTP_PASSWORD=<gmail-app-password>`
- `SMTP_FROM_EMAIL=z1332556430@gmail.com`
- `SMTP_FROM_NAME=AI Paper Summary`
- `SMTP_USE_STARTTLS=true`
- `SMTP_USE_SSL=false`
- `OWNER_ALERT_EMAIL=z1332556430@gmail.com`

## 4. Configure MySQL

```bash
sudo mysql
```

```sql
CREATE DATABASE IF NOT EXISTS ai_paper_summary
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'ai_paper_summary'@'localhost' IDENTIFIED BY '<strong-password>';
GRANT ALL PRIVILEGES ON ai_paper_summary.* TO 'ai_paper_summary'@'localhost';
FLUSH PRIVILEGES;
```

Run schema validation or migration:

```bash
cd /srv/ai-paper-summary/backend
./venv/bin/python scripts/setup_local_db.py
```

For an existing pre-v2.25 database:

```bash
./venv/bin/python scripts/setup_local_db.py --migrate-existing --backfill-title-zh
```

## 5. Build the frontend

```bash
cd /srv/ai-paper-summary/frontend
npm install
npm run build
```

`frontend/.env.production` already points the production build to `/api`.

## 6. Install systemd and nginx configs

```bash
sudo cp /srv/ai-paper-summary/deploy/linux/ai-paper-summary-backend.service /etc/systemd/system/
sudo cp /srv/ai-paper-summary/deploy/linux/ai-paper-summary.nginx.conf /etc/nginx/sites-available/ai-paper-summary
sudo ln -sf /etc/nginx/sites-available/ai-paper-summary /etc/nginx/sites-enabled/ai-paper-summary
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl daemon-reload
sudo systemctl enable ai-paper-summary-backend
sudo systemctl restart ai-paper-summary-backend
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Install cron jobs

```bash
cd /srv/ai-paper-summary/backend
./venv/bin/python scripts/install_linux_cron.py
crontab -l
```

The managed cron block installs:

- `08:00` Asia/Shanghai: `run_daily_update_job.py`
- `08:30` Asia/Shanghai: `send_daily_digest.py`

## 8. Data migration

From the source machine:

```bash
mysqldump --single-transaction --default-character-set=utf8mb4 ai_paper_summary > ai_paper_summary.sql
scp ai_paper_summary.sql ubuntu@43.155.154.193:/tmp/ai_paper_summary.sql
```

On the server:

```bash
mysql -u ai_paper_summary -p ai_paper_summary < /tmp/ai_paper_summary.sql
cd /srv/ai-paper-summary/backend
./venv/bin/python scripts/setup_local_db.py
```

## 9. Verification

```bash
systemctl status ai-paper-summary-backend
sudo systemctl status nginx
curl http://127.0.0.1:8000/
curl http://43.155.154.193/api/v1/papers
```

Manual digest test:

```bash
cd /srv/ai-paper-summary/backend
./venv/bin/python scripts/send_daily_digest.py --issue-date 2026-03-25 --recipient-override z1332556430+briefingtest@gmail.com
```

## 10. Rollback and diagnostics

Common commands:

```bash
sudo journalctl -u ai-paper-summary-backend -n 200 --no-pager
sudo tail -n 200 /var/log/nginx/ai-paper-summary.error.log
tail -n 200 /srv/ai-paper-summary/backend/runtime/logs/daily_update.log
tail -n 200 /srv/ai-paper-summary/backend/runtime/logs/daily_digest.log
```
