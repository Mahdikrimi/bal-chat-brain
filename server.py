
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

from brain import BalBrain

brain = BalBrain()
brain_lock = Lock()


class BALChatServer(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(
            data, ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type", "application/json; charset=utf-8"
        )
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Headers", "Content-Type"
        )
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, OPTIONS"
        )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(200, {"ok": True})

    def do_GET(self):
        if self.path in ("/", "/health"):
            self.send_json(200, {
                "name": "BAL CHAT",
                "status": "online",
                "version": "1.0"
            })
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/chat":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            size = int(self.headers.get("Content-Length", "0"))

            if size <= 0 or size > 1000000:
                self.send_json(400, {"error": "Invalid message size"})
                return

            data = json.loads(
                self.rfile.read(size).decode("utf-8")
            )

            message = data.get("message", "")

            if not isinstance(message, str) or not message.strip():
                self.send_json(400, {"error": "پیام خالی است"})
                return

            with brain_lock:
                answer = brain.reply(message)

            self.send_json(200, {
                "reply": answer,
                "service": "BAL CHAT"
            })

        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"error": "درخواست نامعتبر است"})

        except Exception as error:
            print("Server error:", repr(error), flush=True)
            self.send_json(500, {"error": "خطای داخلی سرور"})

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        BALChatServer
    )

    print("BAL CHAT SERVER STARTED!", flush=True)

    try:
        server.serve_forever()
    finally:
        server.server_close()
        brain.close()
