
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
THRESHOLD = float(os.getenv("ARBITRAGE_THRESHOLD", "0.5"))

# 初始化 OKX 與 KuCoin
okx = ccxt.okx()
kucoin = ccxt.kucoin()
okx.load_markets()
kucoin.load_markets()

print("✅ OKX 支援的幣種（前10個）:", list(okx.symbols)[:10])
print("✅ KuCoin 支援的幣種（前10個）:", list(kucoin.symbols)[:10])

# 傳送測試訊息到 Telegram
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
        print("✅ 測試訊息已送出")
    except Exception as e:
        print("❌ 發送 Telegram 失敗:", e)

send_telegram("🚀 Telegram 測試訊息：Bot 已上線，準備套利監控中。")

# 套利主邏輯（含手續費）
def get_price(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol)
    return ticker['bid'], ticker['ask']

def monitor_arbitrage():
    FEE_RATE = 0.001

    while True:
        try:
            if SYMBOL in okx.symbols and SYMBOL in kucoin.symbols:
                kucoin_bid, kucoin_ask = get_price(kucoin, SYMBOL)
                okx_bid, okx_ask = get_price(okx, SYMBOL)

                buy_price = kucoin_ask * (1 + FEE_RATE)
                sell_price = okx_bid * (1 - FEE_RATE)
                diff = sell_price - buy_price
                profit_ratio = (diff / buy_price) * 100

                print(f"[DEBUG] KuCoin 買(含費): {buy_price:.2f} / OKX 賣(含費): {sell_price:.2f} → 價差: {diff:.2f} USDT | 利潤率: {profit_ratio:.2f}%")

                if diff > THRESHOLD:
                    msg = (
                        f"🚨 {SYMBOL} 套利機會（含手續費）\n"
                        f"📥 KuCoin 買價（含費）: {buy_price:.2f} USDT\n"
                        f"📤 OKX 賣價（含費）: {sell_price:.2f} USDT\n"
                        f"💰 淨價差：{diff:.2f} USDT\n"
                        f"📈 利潤率：{profit_ratio:.2f}%"
                    )
                    send_telegram(msg)
        except Exception as e:
            print("❌ 執行錯誤:", e)

        time.sleep(15)

# Flask Web
app = Flask(__name__)

@app.route("/")
def index():
    return f"{SYMBOL} Arbitrage Debug Bot Running"

if __name__ == "__main__":
    threading.Thread(target=monitor_arbitrage, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
