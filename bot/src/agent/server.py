import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from time import perf_counter

from .brain import decide

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
        LOGGER.info("decision %.2f ms, commands=%d, error=%s",
                    elapsed, len(response["roleCommandMap"]), error)
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
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
