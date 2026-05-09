# UnityBridge

Standalone Python-native client for the
[`youngwoocho02/unity-cli`](https://github.com/youngwoocho02/unity-cli)
Unity Connector protocol.

This package does not call the `unity-cli` binary. It talks directly to the
Unity Connector by:

1. Reading instance heartbeat files from `~/.unity-cli/instances/*.json`.
2. Selecting a running Unity Editor by port, project path, current working
   directory, or most recent heartbeat.
3. Sending JSON to `http://127.0.0.1:{port}/command`.

It is intentionally separate from `D:\Code\Codex\Agent` so it can be tested
and evolved before integration.

## Install for local development

```powershell
cd D:\Code\Codex\CP\UnityBridge
python -m pip install -e .
```

## CLI examples

```powershell
python -m unity_cli_native status
python -m unity_cli_native --json instances
python -m unity_cli_native --json call list
python -m unity_cli_native call console --params '{"lines": 20, "filter": "error,warning,log"}'
python -m unity_cli_native call --project D:\UnityProjects\MyGame editor --params '{"action": "refresh"}'
```

## Python examples

```python
from unity_cli_native import UnityClient

client = UnityClient(project=r"D:\UnityProjects\MyGame")
status = client.status()
print(status.state, status.port)

result = client.call("list")
print(result.success, result.message, result.data)
```

## Run tests

```powershell
cd D:\Code\Codex\CP
python -m unittest discover -s UnityBridge\tests
```
