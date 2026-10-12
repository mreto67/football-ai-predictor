import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
CATALOG = ROOT / "data" / "predictions" / "all_leagues_2026_27_predictions.json"
HOST = "127.0.0.1"
PORT = 8765


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/predictions":
            try:
                data = json.loads(CATALOG.read_text(encoding="utf-8"))
                payload = json.dumps(
                    data, ensure_ascii=False
                ).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(payload)
            except (OSError, json.JSONDecodeError) as exc:
                payload = json.dumps({
                    "error": "Tahmin kataloğu okunamadı",
                    "detail": str(exc),
                }, ensure_ascii=False).encode("utf-8")

                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            return

        if path == "/":
            self.path = "/index.html"

        super().do_GET()

    def log_message(self, fmt, *args):
        print("[web]", fmt % args)


if __name__ == "__main__":
    if not WEB_DIR.is_dir():
        raise SystemExit(f"Web klasörü bulunamadı: {WEB_DIR}")
    if not CATALOG.is_file():
        raise SystemExit(f"Tahmin kataloğu bulunamadı: {CATALOG}")

    print(f"Football AI hazır: http://{HOST}:{PORT}")
    print("Durdurmak için Ctrl+C")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
