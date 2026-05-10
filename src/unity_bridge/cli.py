from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .adapter import UnityActionResult
from .adapter import UnityBridgeAdapter
from .client import CommandResponse
from .client import DiscoveryError
from .client import Instance
from .client import UnityBridgeError
from .client import UnityClient


def add_common_options(
    parser: argparse.ArgumentParser,
    *,
    json_option: bool,
    suppress_defaults: bool,
) -> None:
    default = argparse.SUPPRESS if suppress_defaults else None
    timeout_default = argparse.SUPPRESS if suppress_defaults else 120_000
    parser.add_argument("--project", default=default, help="Select Unity instance by project path substring.")
    parser.add_argument("--port", type=int, default=default, help="Select Unity instance by port.")
    parser.add_argument("--timeout-ms", type=int, default=timeout_default, help="HTTP timeout in milliseconds.")
    parser.add_argument("--instances-dir", default=default, help="Override ~/.unity-bridge/instances.")
    if json_option:
        json_default = argparse.SUPPRESS if suppress_defaults else False
        parser.add_argument("--json", action="store_true", default=json_default, help="Print JSON output.")


def build_parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    add_common_options(parent, json_option=True, suppress_defaults=True)

    parser = argparse.ArgumentParser(prog="unity-bridge")
    add_common_options(parser, json_option=True, suppress_defaults=False)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("instances", parents=[parent], help="List discovered Unity Connector instances.")
    sub.add_parser("status", parents=[parent], help="Show selected Unity Connector instance status.")
    sub.add_parser("tools", parents=[parent], help="List Unity Connector tools.")

    refresh = sub.add_parser("refresh", parents=[parent], help="Refresh Unity assets.")
    refresh.add_argument("--mode", default="if_dirty", choices=["if_dirty", "force"], help="Refresh mode.")
    refresh.add_argument("--force", action="store_true", help="Allow refresh while entering or in play mode.")
    refresh.add_argument("--scope", default="all", help="Refresh scope.")
    refresh.add_argument("--compile", default="none", choices=["none", "request"], help="Request script compilation.")

    console = sub.add_parser("console", parents=[parent], help="Read or clear Unity console logs.")
    console.add_argument("--count", type=int, default=50, help="Maximum number of entries to return.")
    console.add_argument("--type", dest="types", action="append", help="Log type: error, warning, or log. Repeatable.")
    console.add_argument("--stacktrace", default="user", choices=["none", "user", "full"], help="Stack trace output mode.")
    console.add_argument("--clear", action="store_true", help="Clear the Unity console.")

    test = sub.add_parser("test", parents=[parent], help="Run Unity tests.")
    test.add_argument("--mode", default="EditMode", choices=["EditMode", "PlayMode"], help="Unity test mode.")
    test.add_argument("--filter", help="Namespace, class, or full test name filter.")
    test.add_argument("--allow-dirty-scenes", action="store_true", help="Run tests with unsaved scene changes.")
    test.add_argument("--auto-save-scenes", action="store_true", help="Save dirty scenes before running tests.")

    editor = sub.add_parser("editor", parents=[parent], help="Control Unity Editor play state.")
    editor.add_argument("action", choices=["play", "stop", "pause"], help="Editor action.")
    editor.add_argument("--wait", action="store_true", help="Wait until play or stop completes.")

    menu = sub.add_parser("menu", parents=[parent], help="Execute a Unity menu item.")
    menu.add_argument("menu_path", help="Unity menu item path, for example File/Save Project.")

    reserialize = sub.add_parser("reserialize", parents=[parent], help="Force reserialize assets.")
    reserialize.add_argument("paths", nargs="*", help="Optional asset paths. Omit for the entire project.")

    profiler = sub.add_parser("profiler", parents=[parent], help="Control Unity Profiler.")
    profiler.add_argument("action", nargs="?", default="status", help="Profiler action: status, enable, disable, clear, hierarchy.")

    screenshot = sub.add_parser("screenshot", parents=[parent], help="Capture a Unity editor screenshot.")
    screenshot.add_argument("--view", default="scene", choices=["scene", "game"], help="View to capture.")
    screenshot.add_argument("--output-path", help="Output file path.")
    screenshot.add_argument("--width", type=int, help="Screenshot width.")
    screenshot.add_argument("--height", type=int, help="Screenshot height.")

    exec_command = sub.add_parser("exec", parents=[parent], help="Execute arbitrary C# code through Unity.")
    code_group = exec_command.add_mutually_exclusive_group(required=True)
    code_group.add_argument("--code", help="C# code to execute. Use 'return' for output.")
    code_group.add_argument("--code-file", help="Read C# code from a file.")
    exec_command.add_argument("--using", dest="usings", action="append", help="Additional using namespace. Repeatable.")
    exec_command.add_argument("--csc", help="Override csc compiler path.")
    exec_command.add_argument("--dotnet", help="Override dotnet runtime path.")

    call = sub.add_parser("call", parents=[parent], help="Send a command to Unity Connector.")
    call.add_argument("unity_command", help="Unity Connector command name, for example list or console.")
    call.add_argument("--params", default="{}", help="JSON object passed as command params.")

    wait_ready = sub.add_parser("wait-ready", parents=[parent], help="Wait until selected Unity instance is ready.")
    wait_ready.add_argument("--timeout-sec", type=int, default=300, help="Ready wait timeout in seconds.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    client = UnityClient(
        project=getattr(args, "project", None),
        port=getattr(args, "port", None),
        timeout_ms=getattr(args, "timeout_ms", 120_000),
        instances_dir=getattr(args, "instances_dir", None),
    )

    try:
        if args.command == "instances":
            instances = client.scan_instances()
            _print(instances, json_output=args.json)
            return 0

        if args.command == "status":
            instance = client.status()
            _print(instance, json_output=args.json)
            return 0

        adapter = UnityBridgeAdapter(client=client)

        if args.command == "tools":
            response = adapter.list_tools()
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "refresh":
            response = adapter.refresh_assets(
                mode=args.mode,
                force=args.force,
                scope=args.scope,
                compile=args.compile,
            )
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "console":
            response = adapter.clear_console() if args.clear else adapter.read_console(
                count=args.count,
                types=args.types,
                stacktrace=args.stacktrace,
            )
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "test":
            response = adapter.run_tests(
                mode=args.mode,
                filter=args.filter,
                allow_dirty_scenes=args.allow_dirty_scenes,
                auto_save_scenes=args.auto_save_scenes,
            )
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "editor":
            if args.action == "play":
                response = adapter.editor_play(wait=args.wait)
            elif args.action == "stop":
                response = adapter.editor_stop(wait=args.wait)
            else:
                response = adapter.editor_pause()
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "menu":
            response = adapter.execute_menu_item(args.menu_path)
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "reserialize":
            response = adapter.reserialize_assets(args.paths or None)
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "profiler":
            response = adapter.profiler(action=args.action)
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "screenshot":
            response = adapter.screenshot(
                view=args.view,
                output_path=args.output_path,
                width=args.width,
                height=args.height,
            )
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "exec":
            response = adapter.exec_csharp(
                _read_code_arg(args),
                usings=args.usings,
                csc=args.csc,
                dotnet=args.dotnet,
            )
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "call":
            params = _parse_params(args.params)
            response = client.call(args.unity_command, params)
            _print(response, json_output=args.json)
            return 0 if response.success else 1

        if args.command == "wait-ready":
            instance = client.wait_for_ready(timeout_sec=args.timeout_sec)
            _print(instance, json_output=args.json)
            return 0

    except UnityBridgeError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 2


def _read_code_arg(args: argparse.Namespace) -> str:
    if args.code is not None:
        return args.code
    try:
        return Path(args.code_file).read_text(encoding="utf-8")
    except OSError as exc:
        raise DiscoveryError(f"cannot read --code-file: {exc}") from exc


def _parse_params(value: str) -> Any:
    try:
        params = json.loads(value)
    except json.JSONDecodeError as exc:
        raise DiscoveryError(f"--params must be valid JSON: {exc}") from exc
    if params is None:
        return {}
    if not isinstance(params, dict):
        raise DiscoveryError("--params must be a JSON object")
    return params


def _print(value: Any, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(_to_jsonable(value), ensure_ascii=False, indent=2))
        return

    if isinstance(value, list):
        if not value:
            print("No Unity instances found.")
            return
        for instance in value:
            _print_instance(instance)
        return
    if isinstance(value, Instance):
        _print_instance(value)
        return
    if isinstance(value, CommandResponse):
        print(value.message)
        if value.data is not None:
            print(json.dumps(value.data, ensure_ascii=False, indent=2))
        return
    if isinstance(value, UnityActionResult):
        print(value.message)
        if value.data is not None:
            print(json.dumps(value.data, ensure_ascii=False, indent=2))
        return
    print(value)


def _print_instance(instance: Instance) -> None:
    age = instance.heartbeat_age_seconds
    age_label = "unknown" if age is None else f"{age:.1f}s"
    print(f"Unity (port {instance.port}): {instance.state}")
    print(f" Project: {instance.project_path}")
    print(f" Version: {instance.unity_version or 'unknown'}")
    print(f" Connector: {instance.connector_version or 'unknown'}")
    print(f" PID: {instance.pid}")
    print(f" Heartbeat age: {age_label}")


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Instance):
        return value.to_dict()
    if isinstance(value, CommandResponse):
        return value.to_dict()
    if isinstance(value, UnityActionResult):
        return value.to_dict()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
