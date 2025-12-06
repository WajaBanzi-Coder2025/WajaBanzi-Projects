from flask import Flask, request, jsonify
from resend import Resend
import random, time, os

app = Flask(__name__)
resend = Resend(api_key=os.getenv("RESEND_API_KEY"))

cooldowns = {}

def generate_otp():
    return str(random.randint(100000, 999999))

@app.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "email missing"}), 400

    now = time.time()

    # cooldown check
    if email in cooldowns and now < cooldowns[email]:
        wait = int(cooldowns[email] - now)
        return jsonify({"success": False, "cooldown": wait})

    otp = generate_otp()

    body = f"""
-------------------------------------------------------------

                    Your 6 digit code is:

                           {otp}

-------------------------------------------------------------
Due to tight security reasons, to prevent our email from being taken,
this has been sent under the Resend Server default email.

Do NOT share this code with anyone.

Thanks for supporting WajaBanzi™
© 2025 All Rights Reserved.
"""

    resend.emails.send({
        "from": "no-reply@resend.dev",
        "to": email,
        "subject": "This is WajaBanzi's Automated System",
        "text": body,
    })

    cooldowns[email] = now + 60  # 60 sec cooldown

    return jsonify({
        "success": True,
        "otp": otp
    })








