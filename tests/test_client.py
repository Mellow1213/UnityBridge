from __future__ import annotations

import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from unity_bridge import CommandResponse
from unity_bridge import DiscoveryError
from unity_bridge import Instance
from unity_bridge import UnityClient
from unity_bridge import discover_instance
from unity_bridge import find_active_by_port
from unity_bridge import find_by_port
from unity_bridge import scan_instances
from unity_bridge import send_command


def write_instance(directory: Path, name: str, **overrides: object) -> Path:
    payload = {
        "state": "ready",
        "projectPath": "D:/UnityProjects/Game",
        "port": 8090,
        "pid": 1234,
        "unityVersion": "6000.0.0f1",
        "connectorVersion": "0.3.18",
        "timestamp": 1_700_000_000_000,
        "compileErrors": False,
    }
    payload.update(overrides)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class FakeUnityServer:
    def __init__(self, response: bytes, *, status: int = 200) -> None:
        self.received: list[dict[str, object]] = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                outer.received.append(
                    {
                        "path": urlparse(self.path).path,
                        "content_type": self.headers.get("Content-Type"),
                        "body": json.loads(body.decode("utf-8")),
                    }
                )
                self.send_response(status)
                self.end_headers()
                if response:
                    self.wfile.write(response)

            def log_message(self, format: str, *args: object) -> None:
                return

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def port(self) -> int:
        return int(self.server.server_port)

    def __enter__(self) -> "FakeUnityServer":
        self.thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.server.shutdown()
        self.thread.join(timeout=5)
        self.server.server_close()


class DiscoveryTests(unittest.TestCase):
    def test_scan_instances_ignores_invalid_files_and_removes_confirmed_dead_pids(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            alive = write_instance(directory, "alive", pid=111, port=8090)
            dead = write_instance(directory, "dead", pid=222, port=8091)
            (directory / "broken.json").write_text("{", encoding="utf-8")
            (directory / "note.txt").write_text("ignored", encoding="utf-8")

            instances = scan_instances(
                instances_dir=directory,
                process_checker=lambda pid: pid == 222,
            )

            self.assertEqual([instance.port for instance in instances], [8090])
            self.assertTrue(alive.exists())
            self.assertFalse(dead.exists())

    def test_find_by_port_selects_most_recent_even_if_stopped(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            write_instance(directory, "old", port=8090, timestamp=10)
            write_instance(directory, "new", port=8090, state="stopped", timestamp=20)

            instance = find_by_port(8090, instances_dir=directory, process_checker=lambda pid: False)

            self.assertEqual(instance.timestamp, 20)
            self.assertEqual(instance.state, "stopped")

    def test_find_active_by_port_skips_stopped_instances(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            write_instance(directory, "stopped", port=8090, state="stopped", timestamp=20)
            write_instance(directory, "ready", port=8090, state="ready", timestamp=10)

            instance = find_active_by_port(8090, instances_dir=directory, process_checker=lambda pid: False)

            self.assertEqual(instance.state, "ready")

    def test_discover_instance_prefers_project_filter_then_cwd_then_recent(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            write_instance(directory, "game", projectPath="D:/UnityProjects/Game", port=8090, timestamp=10)
            write_instance(directory, "tool", projectPath="D:/UnityProjects/Tool", port=8091, timestamp=20)

            by_project = discover_instance(
                project="UnityProjects/Game",
                instances_dir=directory,
                process_checker=lambda pid: False,
            )
            by_cwd = discover_instance(
                instances_dir=directory,
                cwd="D:/UnityProjects/Game/Assets",
                process_checker=lambda pid: False,
            )
            by_recent = discover_instance(
                instances_dir=directory,
                cwd="D:/Other",
                process_checker=lambda pid: False,
            )

            self.assertEqual(by_project.port, 8090)
            self.assertEqual(by_cwd.port, 8090)
            self.assertEqual(by_recent.port, 8091)

    def test_discover_instance_reports_missing_connector_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "instances"

            with self.assertRaises(DiscoveryError):
                discover_instance(instances_dir=missing)


class HttpClientTests(unittest.TestCase):
    def test_send_command_posts_unity_command_json_and_parses_response(self) -> None:
        payload = json.dumps(
            {
                "success": True,
                "message": "Listed tools",
                "data": [{"name": "console"}],
            }
        ).encode("utf-8")
        with FakeUnityServer(payload) as server:
            instance = Instance(state="ready", project_path="D:/Game", port=server.port, pid=1, timestamp=1)

            response = send_command(instance, "list", {"verbose": True})

            self.assertEqual(
                response,
                CommandResponse(success=True, message="Listed tools", data=[{"name": "console"}]),
            )
            self.assertEqual(server.received[0]["path"], "/command")
            self.assertEqual(server.received[0]["content_type"], "application/json")
            self.assertEqual(
                server.received[0]["body"],
                {"command": "list", "params": {"verbose": True}},
            )

    def test_send_command_accepts_plain_text_response(self) -> None:
        with FakeUnityServer(b"plain ok") as server:
            instance = Instance(state="ready", project_path="D:/Game", port=server.port, pid=1, timestamp=1)

            response = send_command(instance, "editor")

            self.assertEqual(response, CommandResponse(success=True, message="plain ok"))

    def test_send_command_accepts_empty_response(self) -> None:
        with FakeUnityServer(b"") as server:
            instance = Instance(state="ready", project_path="D:/Game", port=server.port, pid=1, timestamp=1)

            response = send_command(instance, "editor")

            self.assertTrue(response.success)
            self.assertIn("connection closed before response", response.message)

    def test_unity_client_discovers_instance_and_calls_command(self) -> None:
        response_body = json.dumps({"success": True, "message": "ok"}).encode("utf-8")
        with TemporaryDirectory() as tmp, FakeUnityServer(response_body) as server:
            directory = Path(tmp)
            write_instance(directory, "game", port=server.port)
            client = UnityClient(instances_dir=directory, process_checker=lambda pid: False)

            response = client.call("status")

            self.assertEqual(response, CommandResponse(success=True, message="ok"))


if __name__ == "__main__":
    unittest.main()
