from flask import Flask, render_template_string
import os
import requests
from datetime import datetime, timedelta

LOG_FILE = "XRMlog.txt"
XMR_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd"

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Monero Mining Log</title>
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: #e0e0e0; padding: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #444; padding: 8px; text-align: left; }
        th { background-color: #1e1e1e; }
        tr:nth-child(even) { background-color: #1f1f1f; }
        h1 { color: #00ffcc; }
        .rate, .deltas { margin-bottom: 20px; font-size: 1.1em; }
        .delta-label { color: #00ffcc; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Latest Mining Log</h1>
    <div class="rate">💰 1 XMR = {{ xmr_price }} USD</div>
    <div class="deltas">
        {% for hours, diff in amt_due_deltas.items() %}
            <div><span class="delta-label">Δ {{ hours }} hrs:</span> {{ diff }} XMR</div>
        {% endfor %}
    </div>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>AmtDue (XMR)</th>
            <th>Hashrate (kH/s)</th>
            <th>MinerWorkerCount</th>
            <th>MinerHashes (kH/s)</th>
            <th>AmtPaid (XMR)</th>
        </tr>
        {% for entry in entries %}
        <tr>
            {% for field in entry %}
            <td>{{ field }}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def parse_log():
    if not os.path.exists(LOG_FILE):
        return []
    entries = []
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()[-500:]  # last 500 lines
        for line in reversed(lines):  # newest first
            parts = line.strip().split("|")
            if len(parts) < 6:
                continue
            ts = parts[0].strip()
            try:
                dt = datetime.fromisoformat(ts)
                amt_due = float(parts[1].split(":")[1].strip().split()[0])
                entries.append((dt, amt_due, [p.strip().split(": ", 1)[-1] for p in parts]))
            except Exception:
                continue
    return entries

def compute_amt_due_deltas(entries):
    now = datetime.now()
    windows = [6, 12, 24, 48]  # hours
    results = {}
    for hours in windows:
        cutoff = now - timedelta(hours=hours)
        window_entries = [e for e in entries if e[0] <= cutoff]
        if window_entries:
            earliest_amt_due = window_entries[-1][1]
            latest_amt_due = entries[0][1]
            delta = latest_amt_due - earliest_amt_due
            results[hours] = f"{delta:.6f}"
        else:
            results[hours] = "N/A"
    return results

def get_xmr_price():
    try:
        resp = requests.get(XMR_API_URL, timeout=5)
        return f"${resp.json()['monero']['usd']:,.2f}"
    except Exception:
        return "Unavailable"

@app.route("/")
def index():
    parsed_entries = parse_log()
    entries = [e[2] for e in parsed_entries]
    xmr_price = get_xmr_price()
    amt_due_deltas = compute_amt_due_deltas(parsed_entries)
    return render_template_string(HTML_TEMPLATE, entries=entries, xmr_price=xmr_price, amt_due_deltas=amt_due_deltas)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)