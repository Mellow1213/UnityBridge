# UnityBridge

[한국어](README.ko.md) | English

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

## Quick Start

### 1. Install the Unity package

In Unity Editor:

1. Open `Window > Package Manager`.
2. Click `+`.
3. Choose `Add package from git URL...`.
4. Paste:

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-connector
```

The connector starts automatically when the Unity Editor opens. It writes
heartbeat files under `~/.unity-cli/instances/`, then the Python client can
discover the running Editor and send commands to `http://127.0.0.1:{port}/command`.

### 2. Install the Python client

```powershell
git clone https://github.com/zjxps2007/UnityBridge.git
cd UnityBridge
python -m pip install -e .
```

### 3. Check the connection

Keep the Unity project open, then run:

```powershell
unity-bridge status
unity-bridge --json instances
unity-bridge --json call list
```

## Unity Package URL

Add the Unity Connector package from this repository:

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-connector
```

To pin a version after tags are published:

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-connector#v0.1.0
```

## CLI Usage

Installed command:

```powershell
unity-bridge status
unity-bridge --json instances
unity-bridge --json call list
```

Module form without installing:

```powershell
$env:PYTHONPATH='D:\Code\Codex\CP\UnityBridge\src'
python -m unity_cli_native status
python -m unity_cli_native --json instances
python -m unity_cli_native --json call list
```

## Command Examples

UnityBridge sends the Unity Connector command name directly.

```powershell
# Enter play mode and wait until Unity confirms it.
unity-bridge call manage_editor --params '{"action":"play","wait_for_completion":true}'

# Stop play mode.
unity-bridge call manage_editor --params '{"action":"stop"}'

# Refresh assets.
unity-bridge call refresh_unity --params '{}'

# Read console logs.
unity-bridge call read_console --params '{"count":20,"types":["error","warning","log"]}'

# Run EditMode tests.
unity-bridge call run_tests --params '{"mode":"EditMode"}'

# Execute a safe Unity menu item.
unity-bridge call execute_menu_item --params '{"menu_path":"File/Save Project"}'
```

Select a specific Unity Editor instance:

```powershell
unity-bridge --project D:\UnityProjects\MyGame status
unity-bridge --port 8090 status
unity-bridge call --project D:\UnityProjects\MyGame read_console --params '{"count":20}'
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
python -m unittest discover -s tests
```

## License

UnityBridge is licensed under the MIT License.

Portions of `unity-connector` are based on the MIT-licensed
`youngwoocho02/unity-cli` Unity Connector. See `NOTICE.md`.
