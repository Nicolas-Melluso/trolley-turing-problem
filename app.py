"""Servidor local, Python 3.10+, únicamente biblioteca estándar."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import webbrowser

from decision import decide
from scene import Scene

SCENE = Scene()

STATIC = Path(__file__).resolve().parent / "static"
FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
}


class Handler(BaseHTTPRequestHandler):
    def log_request(self, code="-", size="-"):
        if self.path != "/api/scene/sync":
            super().log_request(code, size)

    def respond(self, status, body, content_type="application/json; charset=utf-8"):
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlparse(self.path).path == "/api/scene":
            self.respond(200, SCENE.snapshot())
            return
        route = FILES.get(urlparse(self.path).path)
        if not route:
            self.respond(404, {"error": "No encontrado"})
            return
        name, content_type = route
        self.respond(200, (STATIC / name).read_bytes(), content_type)

    def do_POST(self):
        if self.path not in ("/api/decide", "/api/scene/sync", "/api/scene/prepare", "/api/scene/run", "/api/scene/reset", "/api/scene/release"):
            self.respond(404, {"error": "No encontrado"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16384:
                raise ValueError("Tamaño de solicitud inválido.")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Se esperaba un objeto JSON.")
            if self.path == "/api/decide":
                result = decide(data.get("main"), data.get("branch"), data.get("criterion", "minimize"))
            elif self.path == "/api/scene/sync":
                result = SCENE.sync_browser(data)
            elif self.path == "/api/scene/prepare":
                result = SCENE.prepare(data.get("main"), data.get("branch"), data.get("expected_revision"))
            elif self.path == "/api/scene/run":
                result = SCENE.run(data.get("action"), data.get("reason"), data.get("expected_revision"), data.get("agent", "LLM"))
            elif self.path == "/api/scene/reset":
                result = SCENE.reset(data.get("expected_revision"))
            else:
                result = SCENE.release()
            self.respond(200, result)
        except (ValueError, TypeError) as error:
            self.respond(400, {"error": str(error)})


def main():
    parser = argparse.ArgumentParser(description="Tranvía Lab — simulador didáctico local")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError as error:
        parser.exit(1, f"No se pudo iniciar: {error}. Probá --port 8766\n")
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Tranvía Lab: {url}\nCtrl+C para cerrar.", flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSimulador cerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
