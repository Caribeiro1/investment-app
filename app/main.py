from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.templating import Jinja2Templates
import sqlite3, os
from pathlib import Path
import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "investments.db"
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")
SECRET = os.getenv("CRON_SECRET")

app = FastAPI(title="Carteira de Investimentos")
templates = Jinja2Templates(directory="app/templates")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def index(request: Request):
    df = get_conn().execute("SELECT * FROM alocacao").fetchall()
    return templates.TemplateResponse("index.html",
                                      {"request": request, "rows": df})

@app.post("/run-update")
def run_update(x_cron_secret: str = Header("")):
    if x_cron_secret != SECRET:
        raise HTTPException(status_code=401)
    from app.scheduler import update_quotes
    update_quotes()
    return {"status": "updated", "time": datetime.datetime.utcnow()}
