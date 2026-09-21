"""Cliente MCP de prueba: ejecuta una decisión de ejemplo, sin invocar un LLM.

Iniciar app.py primero. Ejecutar: python examples/run_mcp_demo.py
Modifica la escena visible, espera el resultado y lo imprime.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://127.0.0.1:8765")
args = parser.parse_args()
server = Path(__file__).resolve().parents[1] / "mcp_server.py"
process = subprocess.Popen([sys.executable, "-B", str(server), "--url", args.url],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           text=True, encoding="utf-8")
serial = 0


def request(method, params):
    global serial
    serial += 1
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": serial, "method": method, "params": params}) + "\n")
    process.stdin.flush()
    response = json.loads(process.stdout.readline())
    if "error" in response:
        raise RuntimeError(response["error"])
    return response["result"]


def call(name, arguments):
    result = request("tools/call", {"name": name, "arguments": arguments})
    if result.get("isError"):
        raise RuntimeError(result["content"][0]["text"])
    return json.loads(result["content"][0]["text"])


try:
    request("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "demo-client", "version": "1"}})
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()
    scene = call("get_scene", {})
    scene = call("prepare_scene", {"main": scene["main"], "branch": scene["branch"], "expected_revision": scene["revision"]})
    action = "divert" if scene["branch"] < scene["main"] else "keep"
    scene = call("run_decision", {"action": action, "reason": "Prueba del transporte MCP: seleccionar la vía con menos personas. Esta decisión de prueba viene de un script, no de un LLM.", "agent": "Cliente de prueba MCP", "expected_revision": scene["revision"]})
    print("Recorrido iniciado por MCP. Esperando el resultado...", flush=True)
    for _ in range(15):
        time.sleep(1)
        scene = call("get_scene", {})
        if scene["phase"] == "finished":
            print(json.dumps(scene["result"], ensure_ascii=False, indent=2))
            break
    else:
        raise RuntimeError("No terminó el recorrido; revisar el estado del simulador.")
finally:
    process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait(timeout=5)
    process.stdout.close()
