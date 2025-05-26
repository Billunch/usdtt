import os
import time
import ccxt
import requests
import threading
from flask import Flask
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYMBOL = os.getenv("ARBITRAGE_SYMBOL", "BTC/USDT")
THRESHOLD = float(os.getenv("ARBITRAGE_THRESHOLD", "2.0"))

# 初始化 OKX 與 KuCoin
okx = ccxt.okx()
kucoin = ccxt.kucoin()
okx.load_markets()
kucoin.load_markets()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ 發送 Telegram 訊息失敗:", e)

def get_price(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['bid'], ticker['ask']

def monitor_arbitrage():
    while True:
        try:
            if SYMBOL in okx.symbols and SYMBOL in kucoin.symbols:
                kucoin_bid, kucoin_ask = get_price(kucoin, SYMBOL)
                okx_bid, okx_ask = get_price(okx, SYMBOL)

                buy_price = kucoin_ask
                sell_price = okx_bid
                diff = sell_price - buy_price

                print(f"[套利監控] KuCoin 買: {buy_price:.2f} / OKX 賣: {sell_price:.2f} → 價差: {diff:.2f} USDT")

                if diff > THRESHOLD:
                    msg = (
                        f"🚨 {SYMBOL} 套利機會！\n"
                        f"📥 KuCoin 買價: {buy_price:.2f} USDT\n"
                        f"📤 OKX 賣價: {sell_price:.2f} USDT\n"
                        f"💰 價差：{diff:.2f} USDT"
                    )
                    send_telegram(msg)
        except Exception as e:
            print("❌ 執行錯誤:", e)

        time.sleep(15)

app = Flask(__name__)

@app.route("/")
def index():
    return f"{SYMBOL} Arbitrage Monitor Running | Threshold = {THRESHOLD} USDT"

if __name__ == "__main__":
    threading.Thread(target=monitor_arbitrage, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
