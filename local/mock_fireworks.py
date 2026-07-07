"""Mock OpenAI-compatible /chat/completions server to test the container contract
without spending API credits. Echoes which model+category was requested so we can
verify routing end-to-end."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        model = body.get("model", "?")
        system = body.get("messages", [{}])[0].get("content", "")[:40]
        resp = {
            "choices": [{"message": {"content": f"[mock:{model}] sys='{system}'"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }
        data = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("mock fireworks on :8765")
    HTTPServer(("0.0.0.0", 8765), Handler).serve_forever()
