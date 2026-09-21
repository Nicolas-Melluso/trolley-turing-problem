"""Imprime configuración de Codex para la ubicación actual. No escribe archivos."""
import argparse
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://127.0.0.1:8765")
args = parser.parse_args()
print("[mcp_servers.tranvia_lab]")
print("command = " + json.dumps(Path(sys.executable).as_posix(), ensure_ascii=False))
print("args = " + json.dumps(["-B", (Path(__file__).resolve().parent / "mcp_server.py").as_posix(), "--url", args.url], ensure_ascii=False))
print("startup_timeout_sec = 10")
print("tool_timeout_sec = 15")
