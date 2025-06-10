# MoneroData
# ⛏️ Monero Mining Stats Logger & Dashboard

A lightweight Python application for scraping MoneroOcean mining stats and viewing them through a web dashboard. Designed to help miners easily track their mining activity, payouts, and hashrate over time — with optional Discord notifications.

---

## 🧠 Features

- 📡 Polls MoneroOcean’s public API for wallet stats  
- 📝 Logs mining stats to a rotating log file (`XRMlog.txt`)  
- 📬 Sends Discord notifications **only when a payout is received**  
- 🌐 Web dashboard to view live logs in real-time  
- 🔧 Configurable via `config.json`

---

## 🚀 Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/monero-mining-dashboard.git
cd monero-mining-dashboard

2. Install dependencies
Make sure you have Python 3.8+ installed.

bash
pip install flask requests

🛠️ Configuration
Create a config.json file in the project directory:
{
  "wallet_address": "YOUR_MONERO_WALLET_ADDRESS",
  "discord_webhook": "https://discord.com/api/webhooks/your_webhook_url",
  "log_file": "XRMlog.txt",
  "poll_interval_seconds": 1800
}

Replace the wallet address and webhook with your own.

poll_interval_seconds controls how often the API is queried.


▶️ Running the Miner Scraper
This script fetches stats and logs data every poll_interval_seconds.

python advScrape.py
Logs are saved to XRMlog.txt and automatically rotated when the file exceeds ~1MB (up to 5 backups).

A Discord message will be sent when a new payout is detected.

🌐 Running the Log Dashboard
To view logs in a web browser:
python log_dashboard.py
Then open your browser to:

http://localhost:5000
Or from another machine on the network:


http://<your-pi-ip>:5000
You’ll see a table of the most recent 50 log entries.

🧪 Example Log Output
2025-06-09T15:40:36 | AmtDue:   0.005914 XMR | Hashrate:  22.70 kH/s | MinerWorkerCount:  2 | MinerHashes:   45.40 kH/s | AmtPaid:   0.012000 XMR

Running Dashboard in Virtual Python Env

# 1. Install venv if not already installed
sudo apt install python3-venv -y

# 2. Create a virtual environment in your project folder
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Now install your packages safely
pip install flask requests

#5 Deactivate even
deactivate


📌 Future Plans
📈 Plot charts for hashrate & payout history

🔍 Search/filter log table

☁️ Auto-archive old logs

📄 License
MIT — free to use and modify. Credit appreciated!