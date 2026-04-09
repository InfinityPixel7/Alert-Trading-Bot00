import os
import yfinance as yf
import requests
from datetime import datetime

# Credentials
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_msg(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def main():
    ticker = "EURUSD=X"
    # Using 15m interval for the Sniper entry trigger
    df = yf.download(ticker, period="5d", interval="15m", progress=False)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0].lower() for c in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]

    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 15m Sniper Trigger: Strong Wick Rejection
    # Wick is > 60% of candle, price is near daily support/resistance
    wick = abs(curr['high'] - curr['low'])
    lower_wick = min(curr['open'], curr['close']) - curr['low']
    upper_wick = curr['high'] - max(curr['open'], curr['close'])
    
    # Logic: 15m candle rejection + Volume Confirmation
    if lower_wick > (wick * 0.6) and curr['volume'] > curr['volume'].rolling(20).mean().iloc[-1]:
        send_telegram_alert(f"🎯 *15M SNIPER TRIGGER (BUY)*\nPrice: `{curr['close']:.5f}`\n*Action: Place Buy Order!*")
        
    elif upper_wick > (wick * 0.6) and curr['volume'] > curr['volume'].rolling(20).mean().iloc[-1]:
        send_telegram_alert(f"🎯 *15M SNIPER TRIGGER (SELL)*\nPrice: `{curr['close']:.5f}`\n*Action: Place Sell Order!*")

if __name__ == "__main__":
    main()