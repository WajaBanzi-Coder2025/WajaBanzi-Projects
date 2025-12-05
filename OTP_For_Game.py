from flask import Flask, request, jsonify
from email.message import EmailMessage
import smtplib, ssl, random, time, os

SENDER = os.getenv("GMAIL_SENDER")
APP_PASSWORD = os.getenv("GMAIL_PASS")

cooldowns = {}

app = Flask(__name__)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_email(to, otp):
    msg = EmailMessage()
    msg['Subject'] = "Your OTP Code"
    msg['From'] = SENDER
    msg['To'] = to

    body = f"""
-------------------------------------------------------------

                    Your 6 digit code is:

                           {otp}

-------------------------------------------------------------

Do NOT share this code with anyone.

Thanks for supporting WajaBanzi™
© 2025 All Rights Reserved.
"""
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(SENDER, APP_PASSWORD)
        server.send_message(msg)

@app.route("/")
def health_check():
    return jsonify({"status": "alive"})

@app.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "email missing"}), 400

    now = time.time()
    if email in cooldowns and now < cooldowns[email]:
        wait = int(cooldowns[email] - now)
        return jsonify({"success": False, "cooldown": wait})

    otp = generate_otp()
    try:
        send_email(email, otp)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    cooldowns[email] = now + 60  # 60s cooldown

    return jsonify({"success": True, "otp": otp})  # optional: remove otp for security

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

