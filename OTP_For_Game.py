from http.server import BaseHTTPRequestHandler, HTTPServer
from email.message import EmailMessage
import json
import random
import smtplib
import ssl
import time
import os

SENDER = os.getenv("GMAIL_SENDER")
APP_PASSWORD = os.getenv("GMAIL_PASS")

cooldowns = {}

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


class Handler(BaseHTTPRequestHandler):

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def do_POST(self):
        if self.path != "/send_otp":
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')
            return

        content_len = int(self.headers.get("content-length", 0))
        body = self.rfile.read(content_len)
        data = json.loads(body.decode())

        email = data.get("email")
        if not email:
            self._set_headers(400)
            self.wfile.write(b'{"error":"email missing"}')
            return

        now = time.time()

        # cooldown check
        if email in cooldowns and now < cooldowns[email]:
            wait = int(cooldowns[email] - now)
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "success": False,
                "cooldown": wait
            }).encode())
            return

        otp = generate_otp()

        try:
            send_email(email, otp)
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        cooldowns[email] = now + 60  # 60s cooldown

        self._set_headers(200)
        self.wfile.write(json.dumps({
            "success": True,
            "otp": otp  #Debug keep only
        }).encode())


def run():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
