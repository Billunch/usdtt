# Arbitrage Simulation Bot (多幣種模擬套利機器人)

## ✅ 支援功能
- 支援幣種：APT, SUI, ARB
- 比較 KuCoin 與 OKX 價差（雙方向）
- 模擬套利操作（單筆投入上限 300 USDT）
- 利潤率 > 0.5% 才執行模擬
- 自動推送 Telegram 通知
- 自動記錄套利操作到 CSV log

## 🚀 部署方法（Render 免費方案）
1. 上傳本專案到 GitHub
2. Render 建立 Web Service
3. 環境變數：
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
   - MIN_PROFIT_RATE (選填，預設 0.005)
4. Start Command 設為：
   python arbitrage_simulator.py
