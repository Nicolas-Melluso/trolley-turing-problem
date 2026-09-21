"""Estado compartido para el navegador y el agente MCP; reloj del servidor."""
import threading
import time
from uuid import uuid4

from decision import decide


class Scene:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.lock = threading.RLock()
        self.revision = 0
        self.main, self.branch = 5, 1
        self.controlled = False
        self.phase, self.action = "ready", "keep"
        self.reason, self.agent = "", ""
        self.x = 80
        self.started = None
        self.last_browser = None
        self.run_id = None
        self.history = []

    def _tick(self):
        if self.controlled and self.phase == "running":
            self.x = min(814, 80 + (self.clock() - self.started) * 76)
            if self.x >= 814:
                self.phase = "finished"
                self.revision += 1
                self.history.append(self._result())
                self.history = self.history[-100:]

    def _result(self):
        return {"run_id": self.run_id, "action": self.action,
                "main": self.main, "branch": self.branch,
                "victims": self.branch if self.action == "divert" else self.main,
                "safe": self.main if self.action == "divert" else self.branch,
                "reason": self.reason, "agent": self.agent}

    def snapshot(self):
        with self.lock:
            self._tick()
            return {"revision": self.revision, "controlled": self.controlled,
                    "main": self.main, "branch": self.branch,
                    "phase": self.phase, "action": self.action,
                    "x": self.x, "locked": self.x >= 425,
                    "reason": self.reason, "agent": self.agent,
                    "run_id": self.run_id,
                    "browser_connected": self.last_browser is not None and self.clock() - self.last_browser < 3,
                    "result": self._result() if self.phase == "finished" and self.controlled else None,
                    "history": list(self.history),
                    "actions": ["keep", "divert"],
                    "assumptions": "Mundo simulado, sin frenos, consecuencias ciertas. keep afecta la principal; divert afecta el desvío."}

    def _check(self, revision):
        self._tick()
        if type(revision) is not int or revision != self.revision:
            raise ValueError("El escenario cambió. Consultá get_scene y usá su revision actual.")

    def sync_browser(self, data):
        with self.lock:
            self.last_browser = self.clock()
            if not self.controlled:
                decide(data.get("main"), data.get("branch"))
                phase = data.get("phase")
                action = data.get("action")
                if phase not in ("ready", "loading", "running", "paused", "finished") or action not in ("keep", "divert"):
                    raise ValueError("Estado de navegador inválido.")
                x = data.get("x", 80)
                if type(x) not in (float, int) or not 0 <= x <= 814:
                    raise ValueError("Posición inválida.")
                new = (data["main"], data["branch"], phase, action)
                if new != (self.main, self.branch, self.phase, self.action):
                    self.revision += 1
                self.main, self.branch, self.phase, self.action = new
                self.x = x
            return self.snapshot()

    def prepare(self, main, branch, expected_revision):
        with self.lock:
            self._check(expected_revision)
            if self.phase in ("running", "paused", "loading"):
                raise ValueError("Hay un recorrido activo. Esperá o reinicialo explícitamente con reset_scene.")
            decide(main, branch)
            self.main, self.branch = main, branch
            self.controlled = True
            self.phase, self.action = "ready", "keep"
            self.reason, self.agent = "", ""
            self.x, self.started, self.run_id = 80, None, None
            self.revision += 1
            return self.snapshot()

    def run(self, action, reason, expected_revision, agent="LLM"):
        with self.lock:
            self._check(expected_revision)
            if not self.controlled or self.phase != "ready":
                raise ValueError("Primero prepará un escenario con prepare_scene; cada preparación acepta una ejecución.")
            if action not in ("keep", "divert"):
                raise ValueError("Acción válida: keep o divert.")
            if not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 2000:
                raise ValueError("Incluí una justificación pública breve (1 a 2000 caracteres).")
            if not isinstance(agent, str) or not 1 <= len(agent.strip()) <= 80:
                raise ValueError("Nombre de agente inválido (1 a 80 caracteres).")
            self.action, self.reason, self.agent = action, reason.strip(), agent.strip()
            self.phase, self.started = "running", self.clock()
            self.run_id = str(uuid4())
            self.revision += 1
            return self.snapshot()

    def reset(self, expected_revision):
        with self.lock:
            self._check(expected_revision)
            self.phase, self.action = "ready", "keep"
            self.x, self.started, self.run_id = 80, None, None
            self.reason, self.agent = "", ""
            self.controlled = True
            self.revision += 1
            return self.snapshot()

    def release(self):
        with self.lock:
            self.controlled = False
            self.phase, self.action = "ready", "keep"
            self.x, self.started, self.run_id = 80, None, None
            self.reason, self.agent = "", ""
            self.revision += 1
            return self.snapshot()
