"""Reference stub of the model service job API (frontend/src/api/contracts/inference.ts). Stdlib only.

    python3 frontend/tools/stub-model-server/server.py [--port 8000] [--run-seconds 20]

POST /jobs        multipart/form-data, field `slide` (.svs), optional `case_id` → 202 {job_id, status}
GET  /jobs/<id>   → {job_id, status, progress, stage, result | error}
DELETE /jobs/<id> → 204

It does not run a model: the result is a fixed prediction chosen by the TCGA barcode in the uploaded
filename (unknown files get an error prediction). It exists to exercise the frontend's http adapter and to
show the model team the exact wire format the UI expects.
"""

from __future__ import annotations

import argparse
import json
import re
import threading
import time
import uuid
from email.parser import BytesParser
from email.policy import default as email_policy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL_ID = "stub-server-no-model"
FIXTURES = {
    "TCGA-91-8496": ("adenocarcinoma", {"non_tumor": 0.04, "adenocarcinoma": 0.87, "squamous": 0.09}, 412, []),
    "TCGA-52-7810": ("squamous", {"non_tumor": 0.06, "adenocarcinoma": 0.11, "squamous": 0.83}, 1862, []),
    "TCGA-38-7271": ("non_tumor", {"non_tumor": 0.91, "adenocarcinoma": 0.06, "squamous": 0.03}, 738, []),
}
STAGES = [(0.0, "Opening slide"), (0.1, "Detecting tissue"), (0.2, "Tiling tissue"), (0.35, "Analysing tissue regions"), (0.9, "Classifying slide")]

jobs: dict[str, dict] = {}
lock = threading.Lock()
RUN_SECONDS = 20.0


def prediction_for(filename: str) -> dict:
    m = re.search(r"TCGA-[A-Z0-9]{2}-[A-Z0-9]{4}", filename.upper())
    if not m or m.group(0) not in FIXTURES:
        return {"status": "error", "reason": f"Stub server has no fixture for {filename!r}."}
    cls, probs, tiles, warnings = FIXTURES[m.group(0)]
    return {
        "status": "success",
        "predicted_class": cls,
        "class_probabilities": probs,
        "probabilities_calibrated": False,
        "tiles_analyzed": tiles,
        "quality_warnings": warnings,
        "model_identifier": MODEL_ID,
    }


def job_view(job_id: str, job: dict) -> dict:
    if job.get("cancelled"):
        return {"job_id": job_id, "status": "failed", "error": "Job was cancelled."}
    elapsed = time.time() - job["created"]
    if elapsed < 2:
        return {"job_id": job_id, "status": "queued", "progress": None, "stage": None}
    frac = (elapsed - 2) / RUN_SECONDS
    if frac >= 1:
        return {"job_id": job_id, "status": "done", "progress": 1, "stage": None, "result": job["result"]}
    stage = [name for start, name in STAGES if frac >= start][-1]
    return {"job_id": job_id, "status": "running", "progress": round(frac, 3), "stage": stage}


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: dict | None = None) -> None:
        data = b"" if body is None else json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Accept, Content-Type")
        if body is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:  # CORS preflight
        self._send(204)

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/jobs":
            return self._send(404, {"detail": "Not found"})
        length = int(self.headers.get("Content-Length", 0))
        ctype = self.headers.get("Content-Type", "")
        raw = f"Content-Type: {ctype}\r\n\r\n".encode() + self.rfile.read(length)
        msg = BytesParser(policy=email_policy).parsebytes(raw)
        parts = {p.get_param("name", header="content-disposition"): p for p in msg.iter_parts()} if msg.is_multipart() else {}
        slide = parts.get("slide")
        if slide is None or not (slide.get_filename() or "").lower().endswith(".svs"):
            return self._send(400, {"detail": "Expected a multipart field 'slide' with a .svs file."})
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        with lock:
            jobs[job_id] = {"created": time.time(), "result": prediction_for(slide.get_filename())}
        size = len(slide.get_payload(decode=True) or b"")
        print(f"  {job_id}: {slide.get_filename()} ({size} bytes)")
        self._send(202, {"job_id": job_id, "status": "queued"})

    def do_GET(self) -> None:
        m = re.fullmatch(r"/jobs/([\w-]+)", self.path)
        job = m and jobs.get(m.group(1))
        if not job:
            return self._send(404, {"detail": "Unknown job"})
        self._send(200, job_view(m.group(1), job))

    def do_DELETE(self) -> None:
        m = re.fullmatch(r"/jobs/([\w-]+)", self.path)
        if m and m.group(1) in jobs:
            jobs[m.group(1)]["cancelled"] = True
        self._send(204)


def main() -> None:
    global RUN_SECONDS
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--run-seconds", type=float, default=20.0)
    args = ap.parse_args()
    RUN_SECONDS = args.run_seconds
    print(f"stub model server on http://localhost:{args.port} (jobs take ~{RUN_SECONDS + 2:.0f}s)")
    ThreadingHTTPServer(("", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
