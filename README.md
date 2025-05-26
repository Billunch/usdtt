# USDT Arbitrage Bot

This bot monitors arbitrage opportunities between OKX and KuCoin for a given symbol.

## Environment Variables

Refer to `.env.example` or set these in Render:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `ARBITRAGE_SYMBOL` (e.g., BTC/USDT)
- `ARBITRAGE_THRESHOLD` (e.g., 2.0)

## Deployment

Supports deployment to [Render](https://render.com/) using the provided `render.yaml`.
