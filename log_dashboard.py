from flask import Flask, render_template_string
import os

LOG_FILE = "XRMlog.txt"

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
    </style>
</head>
<body>
    <h1>Latest Mining Log</h1>
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
        for line in f.readlines()[-50:]:  # show last 50 lines
            parts = line.strip().split("|")
            if len(parts) < 6:
                continue
            # extract only the value part after ": " from each field
            entries.append([p.strip().split(": ", 1)[-1] for p in parts])
    return entries

@app.route("/")
def index():
    entries = parse_log()
    return render_template_string(HTML_TEMPLATE, entries=entries)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
