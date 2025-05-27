import os
import time
import ccxt
import requests
import threading
import csv
from flask import Flask
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
THRESHOLD = float(os.getenv("MIN_PROFIT_RATE", "0.005"))  # 預設 0.5%
SYMBOLS = ["APT/USDT", "SUI/USDT", "ARB/USDT"]
USDT_CAP = 300  # 單次最大模擬下單金額

okx = ccxt.okx()
kucoin = ccxt.kucoin()
okx.load_markets()
kucoin.load_markets()

log_file = "arbitrage_log.csv"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram 發送失敗:", e)

def get_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['bid'], ticker['ask']
    except:
        return None, None

def log_trade(data):
    header = ["timestamp", "symbol", "buy_ex", "buy_price", "sell_ex", "sell_price", "profit_rate", "usdt_size", "profit"]
    file_exists = os.path.exists(log_file)
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data)

def simulate_arbitrage():
    FEE = 0.001  # 單邊手續費
    while True:
        for symbol in SYMBOLS:
            if symbol in okx.symbols and symbol in kucoin.symbols:
                # 方向一：KuCoin 買 → OKX 賣
                k_bid, k_ask = get_price(kucoin, symbol)
                o_bid, o_ask = get_price(okx, symbol)
                if k_ask and o_bid:
                    buy_price = k_ask * (1 + FEE)
                    sell_price = o_bid * (1 - FEE)
                    profit_rate = (sell_price - buy_price) / buy_price
                    if profit_rate > THRESHOLD:
                        coin_size = USDT_CAP / buy_price
                        profit = (sell_price - buy_price) * coin_size
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        msg = (
                            f"🚨 套利機會 {symbol}\n"
                            f"📥 買: KuCoin {buy_price:.4f}\n"
                            f"📤 賣: OKX {sell_price:.4f}\n"
                            f"📈 利潤率: {profit_rate:.2%}\n"
                            f"💰 模擬下單金額: {USDT_CAP} USDT\n"
                            f"💵 預估淨利: {profit:.2f} USDT"
                        )
                        send_telegram(msg)
                        log_trade([timestamp, symbol, "KuCoin", buy_price, "OKX", sell_price, f"{profit_rate:.4f}", USDT_CAP, f"{profit:.2f}"])

                # 方向二：OKX 買 → KuCoin 賣
                if o_ask and k_bid:
                    buy_price = o_ask * (1 + FEE)
                    sell_price = k_bid * (1 - FEE)
                    profit_rate = (sell_price - buy_price) / buy_price
                    if profit_rate > THRESHOLD:
                        coin_size = USDT_CAP / buy_price
                        profit = (sell_price - buy_price) * coin_size
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        msg = (
                            f"🚨 套利機會 {symbol}\n"
                            f"📥 買: OKX {buy_price:.4f}\n"
                            f"📤 賣: KuCoin {sell_price:.4f}\n"
                            f"📈 利潤率: {profit_rate:.2%}\n"
                            f"💰 模擬下單金額: {USDT_CAP} USDT\n"
                            f"💵 預估淨利: {profit:.2f} USDT"
                        )
                        send_telegram(msg)
                        log_trade([timestamp, symbol, "OKX", buy_price, "KuCoin", sell_price, f"{profit_rate:.4f}", USDT_CAP, f"{profit:.2f}"])
        time.sleep(15)

# Render Flask Web Server 偽裝用
app = Flask(__name__)

@app.route("/")
def index():
    return "Arbitrage Simulation Bot Running"

if __name__ == "__main__":
    threading.Thread(target=simulate_arbitrage, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
