from flask import Flask, request, jsonify
from twilio.rest import Client
from datetime import datetime
import random

app = Flask(__name__)

# === Twilio Configuration ===
TWILIO_ACCOUNT_SID = 'ACc71a1cfeda69b90707a8fdf0806da159'
TWILIO_AUTH_TOKEN = '08888e163f2820f54e3953d8a7d6c27f'
TWILIO_SANDBOX_NUMBER = '+14155238886'
USER_PHONE_NUMBER = 'whatsapp:+256752721686'

# === Twilio Client Setup ===
def get_twilio_client():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return client, TWILIO_SANDBOX_NUMBER

# === Sentiment Analysis (Scaled 1–10) ===
def analyze_sentiment(pair, message):
    score = 5
    msg = message.lower()
    if "bullish" in msg: score += 2
    if "bearish" in msg: score -= 2
    if "liquidity" in msg: score += 1
    if "order block" in msg: score += 1
    if "divergence" in msg: score -= 1
    if "exhaustion" in msg or "pullback" in msg: score -= 1
    return max(1, min(score, 10))

# === Sentiment Label ===
def sentiment_label(score):
    if score >= 8: return "Strong Buy 🟢"
    elif score >= 6: return "Moderate Buy 🟡"
    elif score >= 4: return "Neutral ⚪"
    elif score >= 2: return "Moderate Sell 🔵"
    else: return "Strong Sell 🔴"

# === OANDA Confidence Boost (Simulated) ===
def oanda_confidence_boost(pair):
    boost = {
        "eurusd": 2,
        "usdjpy": 2,
        "btcusd": 3,
        "xauusd": 4
    }
    return boost.get(pair.lower(), 1)

# === Gold Trader Insight (Simulated) ===
def get_gold_insight():
    insights = [
        "🪙 Gold is flexing hard — central banks are watching.",
        "📈 Royal Gold says: breakout brewing above $2000.",
        "🔥 AltSignals: bullish momentum confirmed with order block support.",
        "💡 SmartT AI: gold sentiment is 72% bullish this week."
    ]
    return random.choice(insights)

# === Joke Generator ===
def get_trade_joke(pair, action):
    jokes = {
        "buy": [
            "Why did the trader marry EURUSD? Stable relationship goals.",
            "Buying BTC? Hope your heart is as strong as your wallet.",
            "Gold buyers be like: 'Shiny things make me happy.'"
        ],
        "sell": [
            "Selling USDJPY? Say goodbye like a polite samurai.",
            "BTC sellers: 'I loved you... but I love profits more.'",
            "Gold sellers: 'Time to cash in before it melts!'"
        ],
        "neutral": [
            "No signal? Even the market needs a nap.",
            "Neutral zone: where traders sip coffee and wait.",
            "Sometimes the best trade is no trade. Zen mode activated."
        ]
    }
    return random.choice(jokes.get(action.lower(), jokes["neutral"]))

# === Strategy Engine ===
def detect_strategy(message):
    msg = message.lower()
    strategies = []
    if "trend" in msg or "momentum" in msg: strategies.append("Trend")
    if "divergence" in msg or "pullback" in msg or "exhaustion" in msg: strategies.append("Scalping")
    if "breakout" in msg or "liquidity" in msg or "range expansion" in msg: strategies.append("Breakout")
    if "volatility" in msg: strategies.append("Volatility Spike")
    return strategies if strategies else ["Unclassified"]

# === Risk Filter ===
def risk_filter(sentiment_score, confidence, strategies):
    if sentiment_score <= 3 and confidence <= 5:
        return False
    if "Unclassified" in strategies:
        return False
    return True

# === Signal Generator ===
def generate_signal(pair, message, sentiment_score):
    msg = message.lower()
    action = "neutral"
    emoji = "⚪"
    confidence = 5

    if "bullish" in msg:
        action = "buy"
        emoji = "🟢"
        confidence = 7
    elif "bearish" in msg:
        action = "sell"
        emoji = "🔴"
        confidence = 7

    confidence += oanda_confidence_boost(pair)
    confidence = max(1, min(confidence, 10))

    return {
        "action": action,
        "text": f"{action.upper()} {pair.upper()} {emoji} (Confidence: {confidence}/10)",
        "confidence": confidence
    }

# === WhatsApp Notification ===
def send_whatsapp_notification(pair, signal, sentiment_score, alert_message, strategies, risk_passed):
    try:
        client, from_number = get_twilio_client()
        joke = get_trade_joke(pair, signal["action"])
        gold_commentary = get_gold_insight() if pair.lower() == "xauusd" else ""
        sentiment_banner = sentiment_label(sentiment_score)
        strategy_text = " + ".join(strategies)
        risk_status = "✅ Passed" if risk_passed else "❌ Blocked"

        message_body = f"""🎯 *{pair.upper()} Trading Signal*

{signal['text']}

📊 *Market Sentiment:* {sentiment_banner}
📢 *Strategy:* {strategy_text}
🛡️ *Risk Filter:* {risk_status}
{gold_commentary}

😂 *Joke of the Trade:* {joke}

⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

💡 Stay sharp, legend. This bot runs on pure alpha."""
        message = client.messages.create(
            body=message_body,
            from_=f'whatsapp:{from_number}',
            to=USER_PHONE_NUMBER
        )
        print(f"[SUCCESS] WhatsApp message sent: {message.sid}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send WhatsApp message: {e}")
        return False

# === Home Page ===
@app.route('/')
def home():
    return "✅ Ultimate Trading Bot is running. Webhook ready at /webhook"

# === Webhook Endpoint ===
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if not data or "message" not in data or "pair" not in data:
            return jsonify({"error": "Missing 'message' or 'pair' field"}), 400

        pair = data["pair"].lower()
        alert_message = data["message"]
        sentiment_score = analyze_sentiment(pair, alert_message)
        strategies = detect_strategy(alert_message)
        signal = generate_signal(pair, alert_message, sentiment_score)
        risk_passed = risk_filter(sentiment_score, signal["confidence"], strategies)

        print(f"[{datetime.now()}] Alert: {pair.upper()} | {alert_message[:50]}... | Sentiment: {sentiment_score} | Signal: {signal['text']} | Risk: {risk_passed}")

        if risk_passed:
            send_whatsapp_notification(pair, signal, sentiment_score, alert_message, strategies, risk_passed)

        return jsonify({
            "status": "received",
            "pair": pair.upper(),
            "signal": signal["text"],
            "sentiment": sentiment_score,
            "strategies": strategies,
            "risk_passed": risk_passed,
            "whatsapp_sent": risk_passed
        })

    except Exception as e:
        print(f"[ERROR] Webhook failed: {e}")
        return jsonify({"error": "Internal server error"}), 500

# === Run the App ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
