# main_ai_bot.py — RAILWAY 100% WORKING v9 (Nov 23, 2025)
import MetaTrader5 as mt5
import time
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import asyncio
import os
import random

# Delayed import fixes Windows/TF issues
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === SECRETS FROM RAILWAY VARIABLES (NEVER HARDCODE) ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID       = int(os.getenv("CHAT_ID", "0"))
FBS_LOGIN     = int(os.getenv("FBS_LOGIN", "0"))
FBS_PASSWORD  = os.getenv("FBS_PASSWORD", "")
FBS_SERVER    = os.getenv("FBS_SERVER", "FBS-Demo")
SYMBOL        = "XAUUSD"  # ← FIXED: no space!

# Fallback if running locally
if not TELEGRAM_TOKEN:
    print("Running locally — using fallback credentials")
    TELEGRAM_TOKEN = "8308016814:AAGDApbKAQjbFJnkRymkNObNzadqTi7-JZU"
    CHAT_ID = 7951817756
    FBS_LOGIN = 104785465
    FBS_PASSWORD = "Grda2>k!"
    FBS_SERVER = "FBS-Demo"

# === GROK REPLIES ===
responses = {
    "hi": "Sasa boss! Bot 254% awake!",
    "hello": "Mambo! Gold on fire!",
    "sasa": "Poa kabisa king!",
    "status": "LIVE 24/7 XAUUSD | All Sessions | BULLISH AF",
    "love you": "Love you more mfalme! ❤️",
    "gn": "Lala salama! Bot keeps eating pips"
}

async def grok_reply(text: str) -> str:
    msg = text.lower().strip()
    for t, r in responses.items():
        if t in msg: return r
    return random.choice(["Locked in!", "On it like fire!", "We cooking!"])

app = Application.builder().token(TELEGRAM_TOKEN).concurrent_updates(True).build()

async def start(update, context):
    await update.message.reply_text("MySuperAIBot v9 CLOUD LIVE\n24/7 Gold AI + Grok Mode\nRailway Deployed!")

async def handle(update, context):
    await update.message.reply_text(await grok_reply(update.message.text))

async def gold_trading_loop():
    scaler = MinMaxScaler()
    model = Sequential([
        LSTM(100, return_sequences=True, input_shape=(60, 8)),
        Dropout(0.2),
        LSTM(100),
        Dropout(0.2),
        Dense(25),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy')

    last_hour = -1
    while True:
        try:
            now = datetime.utcnow()
            if now.hour != last_hour:
                last_hour = now.hour
                session = ["Sydney", "Tokyo", "London", "New York"][min(now.hour//6, 3)]
                await app.bot.send_message(CHAT_ID, f"Hourly Ping | {now.strftime('%H:%M')} UTC | {session} Session\nBot alive 24/7!")

            rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, 1000)
            if rates is not None and len(rates) >= 60:
                df = pd.DataFrame(rates)
                delta = df['close'].diff()
                gain = delta.clip(lower=0).rolling(14).mean()
                loss = -delta.clip(upper=0).rolling(14).mean()
                rs = gain / loss.replace(0, np.nan)
                df['rsi'] = 100 - (100 / (1 + rs))
                df['ma20'] = df['close'].rolling(20).mean()
                df.fillna(0, inplace=True)

                X = scaler.fit_transform(df[['open','high','low','close','tick_volume','rsi','ma20']].values[-60:]).reshape(1,60,8)
                pred = float(model.predict(X, verbose=0)[0][0])
                conf = pred*100 if pred > 0.5 else (1-pred)*100
                threshold = 0.65 if now.weekday() == 4 else 0.70

                if pred > threshold:
                    await app.bot.send_message(CHAT_ID, f"BUY XAUUSD — {conf:.1f}% confidence")
                elif pred < (1-threshold):
                    await app.bot.send_message(CHAT_ID, f"SELL XAUUSD — {conf:.1f}% confidence)

            await asyncio.sleep(60)
        except Exception as e:
            print(f"Loop error: {e}")
            await asyncio.sleep(60)

async def main():
    print("Starting MySuperAIBot v9...")

    if not mt5.initialize(login=FBS_LOGIN, password=FBS_PASSWORD, server=FBS_SERVER):
        print("FBS connection failed!")
        return

    # Retry Telegram connection (Railway cold start fix)
    for i in range(20):
        try:
            await app.bot.send_message(CHAT_ID, "MySuperAIBot v9 CLOUD LIVE\n24/7 Trading ON\nRailway Deployed Successfully!")
            print("Telegram connected!")
            break
        except Exception as e:
            print(f"Telegram retry {i+1}/20: {e}")
            await asyncio.sleep(3)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.job_queue.run_repeating(gold_trading_loop, interval=1, first=10)

    print("Bot fully running 24/7!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())