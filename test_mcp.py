import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer

import app
from mcp_server import dispatch
from scene import Scene


class SceneTests(unittest.TestCase):
    def setUp(self):
        self.now = 100
        self.scene = Scene(clock=lambda: self.now)

    def test_lifecycle_and_result_without_browser(self):
        prepared = self.scene.prepare(5, 1, 0)
        started = self.scene.run("divert", "Reducir víctimas previstas.", prepared["revision"], "Test")
        self.assertEqual(started["phase"], "running")
        self.assertFalse(started["browser_connected"])
        self.now += 10
        result = self.scene.snapshot()
        self.assertEqual(result["result"]["victims"], 1)
        self.assertEqual(result["result"]["safe"], 5)
        self.assertEqual(len(self.scene.snapshot()["history"]), 1)

    def test_stale_revision_and_duplicate_execution(self):
        self.scene.prepare(5, 1, 0)
        with self.assertRaises(ValueError):
            self.scene.run("divert", "A", 0)
        self.scene.run("divert", "A", 1)
        with self.assertRaises(ValueError):
            self.scene.run("keep", "B", 1)
        with self.assertRaises(ValueError):
            self.scene.run("keep", "B", 2)

    def test_browser_cannot_overwrite_agent_and_can_release(self):
        self.scene.prepare(5, 1, 0)
        data = self.scene.sync_browser({"main": 12, "branch": 12, "phase": "ready", "action": "keep"})
        self.assertEqual(data["main"], 5)
        self.assertTrue(data["browser_connected"])
        self.scene.release()
        with self.assertRaises(ValueError):
            self.scene.run("divert", "A", 1)
        data = self.scene.sync_browser({"main": 2, "branch": 3, "phase": "ready", "action": "keep"})
        self.assertEqual(data["main"], 2)

    def test_running_scene_requires_explicit_reset(self):
        self.scene.prepare(5, 1, 0)
        self.scene.run("keep", "No intervención.", 1)
        with self.assertRaises(ValueError):
            self.scene.prepare(1, 5, 2)
        ready = self.scene.reset(2)
        self.assertEqual(ready["phase"], "ready")

    def test_invalid_reason_and_action(self):
        self.scene.prepare(5, 1, 0)
        for action, reason in [("stop", "A"), ("keep", " "), ("keep", "a" * 2001)]:
            with self.assertRaises(ValueError):
                self.scene.run(action, reason, 1)
        self.assertEqual(self.scene.snapshot()["phase"], "ready")


class ProtocolTests(unittest.TestCase):
    def test_notifications_and_errors(self):
        self.assertIsNone(dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"}, ""))
        self.assertEqual(dispatch([], "")["error"]["code"], -32600)
        unknown = dispatch({"jsonrpc": "2.0", "id": 1, "method": "absent"}, "")
        self.assertEqual(unknown["error"]["code"], -32601)

    def test_real_stdio_to_http_bridge(self):
        original = app.SCENE
        app.SCENE = Scene()
        server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            messages = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_scene", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "prepare_scene", "arguments": {"main": 5, "branch": 1, "expected_revision": 0}}},
                {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "run_decision", "arguments": {"action": "divert", "reason": "Reducir víctimas — prueba UTF-8.", "expected_revision": 1}}},
                {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "run_decision", "arguments": {"action": "keep", "reason": "Duplicado", "expected_revision": 1}}},
            ]
            result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("mcp_server.py")), "--url", f"http://127.0.0.1:{server.server_port}"],
                                    input="\n".join(json.dumps(item) for item in messages) + "\n",
                                    text=True, encoding="utf-8", capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            responses = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual(len(responses), 6)
            self.assertEqual(len(responses[1]["result"]["tools"]), 4)
            self.assertFalse(responses[4]["result"]["isError"])
            self.assertTrue(responses[5]["result"]["isError"])
            current = app.SCENE.snapshot()
            self.assertEqual(current["action"], "divert")
            self.assertEqual(current["reason"], "Reducir víctimas — prueba UTF-8.")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            app.SCENE = original


if __name__ == "__main__":
    unittest.main()
