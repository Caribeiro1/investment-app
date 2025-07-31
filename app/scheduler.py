import sqlite3, os, datetime, json, requests
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "investments.db"
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")

def update_quotes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS quotes (ticker TEXT, price REAL, ts TEXT)")
    tickers = [r[0] for r in cur.execute("SELECT DISTINCT ticker FROM carteira_acoes")]
    for t in tickers:
        url = (f"https://www.alphavantage.co/query?"
               f"function=TIME_SERIES_DAILY_ADJUSTED&symbol={t}.SA&apikey={ALPHA_KEY}")
        data = requests.get(url, timeout=30).json()
        if "Time Series (Daily)" in data:
            day = next(iter(data["Time Series (Daily)"]))
            price = float(data["Time Series (Daily)"][day]["4. close"])
            cur.execute("INSERT INTO quotes VALUES (?,?,?)",
                        (t, price, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    print("Quotes updated!")

if __name__ == "__main__":
    update_quotes()
