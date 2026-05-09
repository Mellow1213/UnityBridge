# UnityBridge

Python-native client and Unity package for the
[`youngwoocho02/unity-cli`](https://github.com/youngwoocho02/unity-cli)
Unity Connector protocol.

The Python client does not call the `unity-cli` binary. It talks directly to
the Unity Connector by:

1. Reading instance heartbeat files from `~/.unity-cli/instances/*.json`.
2. Selecting a running Unity Editor by port, project path, current working
   directory, or most recent heartbeat.
3. Sending JSON to `http://127.0.0.1:{port}/command`.

It is intentionally separate from `D:\Code\Codex\Agent` so it can be tested
and evolved before integration.

## Unity setup

Add the Unity Connector package from this repository:

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-connector
```

In Unity:

1. Open `Window > Package Manager`.
2. Click `+`.
3. Choose `Add package from git URL...`.
4. Paste the URL above.

The connector starts automatically when the Unity Editor opens. It writes
heartbeat files under `~/.unity-cli/instances/`, then the Python client can
discover the running Editor and send commands to `http://127.0.0.1:{port}/command`.

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
python -m unity_cli_native call read_console --params '{"count": 20, "types": ["error", "warning", "log"]}'
python -m unity_cli_native call --project D:\UnityProjects\MyGame manage_editor --params '{"action": "play", "wait_for_completion": true}'
python -m unity_cli_native call refresh_unity --params '{}'
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
