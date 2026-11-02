#!/usr/bin/env python3
"""Local browser workflow for publishing event image galleries."""

import argparse
import json
import shutil
import sys
import tempfile
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# AI-generated: serve the local upload, preview, and finalize workflow.
from tools.event_publish import PublishError, load_workflow_config, publish_event


# AI-generated: parse browser multipart fields without the removed cgi module.
def parse_multipart(request):
    content_type = request.headers.get("Content-Type", "")
    content_length = int(request.headers.get("Content-Length", "0"))
    body = request.rfile.read(content_length)
    envelope = (
        f"Content-Type: {content_type}\r\n"
        "MIME-Version: 1.0\r\n\r\n"
    ).encode("utf-8") + body
    message = BytesParser(policy=default).parsebytes(envelope)
    fields = {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        filename = part.get_filename()
        value = part.get_payload(decode=True) if filename else part.get_content()
        if filename:
            fields.setdefault(name, []).append({"filename": filename, "content": value or b""})
        else:
            fields[name] = value
    return fields


class WorkflowHandler(BaseHTTPRequestHandler):
    server_version = "NatureClubEventWorkflow/1.0"

    def _send(self, status, payload, content_type="application/json"):
        body = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/" or self.path == "/index.html":
            page = (Path(__file__).parent / "event_workflow.html").read_bytes()
            self._send(200, page, "text/html; charset=utf-8")
            return
        if self.path == "/api/config":
            self._send(200, json.dumps(load_workflow_config(self.server.root)))
            return
        self._send(404, json.dumps({"error": "Not found"}))

    def do_POST(self):  # noqa: N802
        if self.path not in {"/api/preview", "/api/finalize"}:
            self._send(404, json.dumps({"error": "Not found"}))
            return
        temporary = Path(tempfile.mkdtemp(prefix=".event-upload-", dir=self.server.root))
        try:
            form = parse_multipart(self)
            manifest = json.loads(form.get("manifest", "{}"))
            images = []
            uploads = form.get("images", [])
            for index, upload in enumerate(uploads, start=1):
                if not upload.get("filename"):
                    continue
                source = temporary / f"upload-{index}{Path(upload['filename']).suffix.lower()}"
                source.write_bytes(upload["content"])
                item = manifest.get("images", [])[index - 1] if index - 1 < len(manifest.get("images", [])) else {}
                images.append({**item, "source": str(source), "name": item.get("name") or upload["filename"]})
            result = publish_event(
                self.server.root,
                manifest.get("title", ""),
                manifest.get("date", ""),
                manifest.get("tags", []),
                manifest.get("author"),
                images,
                manifest.get("options", {}),
                commit=self.path == "/api/finalize",
            )
            self._send(200, json.dumps({"ok": True, "result": result}))
        except (PublishError, ValueError, OSError, KeyError, TypeError) as error:
            self._send(400, json.dumps({"ok": False, "error": str(error)}))
        finally:
            shutil.rmtree(temporary, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--port", type=int, default=8765, help="Local port")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), WorkflowHandler)
    server.root = args.root.resolve()
    print(f"Event workflow: http://127.0.0.1:{args.port}/")
    print("Only local browser connections can reach this repository-writing tool.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped event workflow.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()