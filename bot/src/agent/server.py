import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from time import perf_counter

from .brain import decide
from .protocol import DAY_ROUNDS, ROUNDS_PER_DAY

LOGGER = logging.getLogger(__name__)
TRACE_LOCK = Lock()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        started = perf_counter()
        payload = None
        response = {"roleCommandMap": {}}
        error = None
        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
            response["roleCommandMap"] = decide(payload)
        except Exception as exc:
            error = type(exc).__name__ + ": " + str(exc)
            LOGGER.exception("decision failed; returning empty commands")
        elapsed = (perf_counter() - started) * 1000
        body = json.dumps(response, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()
        state = payload if isinstance(payload, dict) else {}
        round_no = state.get("roundNo")
        phase = ("day" if (round_no - 1) % ROUNDS_PER_DAY < DAY_ROUNDS else "night") if isinstance(round_no, int) else "unknown"
        team = state.get("teamOur")
        team = team if isinstance(team, dict) else {}
        roles = team.get("roles")
        roles = roles if isinstance(roles, list) else []
        base_hp = next((role.get("health") for role in roles
                        if isinstance(role, dict) and role.get("roleType") == "station"), None)
        units = [(role.get("id"), role.get("roleType"), role.get("health"))
                 for role in roles if isinstance(role, dict)
                 and role.get("roleType") in {"worker", "pioneer", "gatling", "railgun", "rocket"}]
        results = state.get("lastRoundRoleActionResults")
        results = results if isinstance(results, dict) else {}
        invalid = [str(uid) for uid, valid in results.items() if valid is False]
        robots = state.get("robot")
        robots = robots.get("roles") if isinstance(robots, dict) else None
        LOGGER.info("round %s | phase=%s base_hp=%s gold=%s units=%s robots=%d last_invalid=%s errors=%s | commands=%s | %.2f ms error=%s",
                    round_no, phase, base_hp, team.get("goldNum"), units,
                    len(robots) if isinstance(robots, list) else 0,
                    invalid, str(state.get("errors") or [])[:500],
                    response["roleCommandMap"], elapsed, error)
        # Opt-in local evidence; no outgoing network call or external model SDK.
        trace = os.environ.get("COMPETITION_TRACE")
        if trace:
            try:
                with TRACE_LOCK:
                    path = Path(trace)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("a", encoding="utf-8") as stream:
                        stream.write(json.dumps({
                            "request": payload, "response": response,
                            "decisionMs": round(elapsed, 3), "error": error,
                        }, ensure_ascii=False) + "\n")
            except Exception:
                LOGGER.exception("could not write trace")

    def log_message(self, format: str, *args) -> None:
        return


def serve(port: int) -> None:
    with ThreadingHTTPServer(("0.0.0.0", port), Handler) as server:
        LOGGER.info("listening on 0.0.0.0:%d", server.server_port)
        server.serve_forever()
