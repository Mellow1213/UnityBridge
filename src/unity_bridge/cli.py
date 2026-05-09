from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

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
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
