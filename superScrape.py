import requests
from datetime import datetime
import time
import json
import os
import logging
from logging.handlers import RotatingFileHandler

# Load config
CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def send_discord_notification(webhook_url, message):
    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Discord webhook failed: {e}")

def fetch_data(wallet_address):
    api_main = f"https://api.moneroocean.stream/miner/{wallet_address}/stats"
    api_workers = f"https://api.moneroocean.stream/miner/{wallet_address}/stats/allWorkers"
    try:
        main_stats = requests.get(api_main).json()
        worker_stats = requests.get(api_workers).json()
        return main_stats, worker_stats
    except requests.RequestException as e:
        print(f"[ERROR] API fetch failed: {e}")
        return None, None

def setup_logger(log_file):
    logger = logging.getLogger("minerLogger")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def log_data(main_data, worker_data, logger):
    timestamp = datetime.now().isoformat()

    dash_due = main_data.get("amtDue", 0)
    hashrate = main_data.get("hash", 0)
    amt_paid = main_data.get("amtPaid", 0)
    dash_due_xmr = dash_due / 1e12
    hashrate_khs = hashrate / 1000
    total_amtpd = amt_paid / 1e12

    workers = worker_data if isinstance(worker_data, dict) else {}
    worker_count = len([k for k in workers if k != "global"])
    total_hashes = workers.get("global", {}).get("hash", 0)
    total_hashrate_khs = total_hashes / 1000

    log_line = (
        f"{timestamp} | AmtDue: {dash_due_xmr:>10.6f} XMR | Hashrate: {hashrate_khs:>6.2f} kH/s | "
        f"MinerWorkerCount: {worker_count:>2} | MinerHashes: {total_hashrate_khs:>7.2f} kH/s | "
        f"AmtPaid: {total_amtpd:>10.6f} XMR"
    )

    logger.info(log_line)
    print("[LOGGED]", log_line)

    return amt_paid  # return value to check payout changes

def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] Missing config file: {CONFIG_FILE}")
        return

    config = load_config()
    wallet = config["wallet_address"]
    webhook = config["discord_webhook"]
    log_file = config.get("log_file", "ssXRMlog.txt")
    poll_interval = config.get("poll_interval_seconds", 1800)

    logger = setup_logger(log_file)

    main_data, worker_data = fetch_data(wallet)
    if not main_data or not worker_data:
        print("[ERROR] Failed to fetch initial stats. Exiting.")
        return

    last_amt_paid = main_data.get("amtPaid", 0)

    while True:
        main_data, worker_data = fetch_data(wallet)
        if main_data and worker_data:
            current_amt_paid = main_data.get("amtPaid", 0)

            if current_amt_paid > last_amt_paid:
                paid_diff = (current_amt_paid - last_amt_paid) / 1e12
                timestamp = datetime.now().isoformat()
                message = f"💸 Payout Detected!\nNew payment: +{paid_diff:.6f} XMR"
                send_discord_notification(webhook, message)

                # Also log payout event
                logger.info(f"{timestamp} | 💸 Payout Detected: +{paid_diff:.6f} XMR")

            last_amt_paid = current_amt_paid
            log_data(main_data, worker_data, logger)

        time.sleep(poll_interval)

if __name__ == "__main__":
    main()
