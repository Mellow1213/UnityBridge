# UnityBridge

[한국어](README.ko.md) | English

Python-native client and Unity package for controlling the Unity Editor through
a local HTTP connector.

The Python client does not require a separate CLI binary. It talks directly to
the Unity connector by:

1. Reading instance heartbeat files from `~/.unity-bridge/instances/*.json`.
2. Selecting a running Unity Editor by port, project path, current working
   directory, or most recent heartbeat.
3. Sending JSON to `http://127.0.0.1:{port}/command`.

It is intentionally separate from `D:\Code\Codex\Agent` so it can be tested
and evolved before integration.

## Quick Start

### 1. Install the Unity package

In Unity Editor, open `Window > Package Manager > + > Add package from git URL...`
and paste:

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-bridge-connector
```

The connector starts automatically when the Unity Editor opens. It writes
heartbeat files under `~/.unity-bridge/instances/`, then the Python client can
discover the running Editor and send commands to `http://127.0.0.1:{port}/command`.

### 2. Install the Python client

```powershell
python -m pip install --upgrade "git+https://github.com/zjxps2007/UnityBridge.git"
```

If this repository is public, the PowerShell installer can also be run directly:

```powershell
irm https://raw.githubusercontent.com/zjxps2007/UnityBridge/main/install.ps1 | iex
```

For private repositories, `raw.githubusercontent.com` requires authentication and
may return `404`. In that case, use the `pip install` command above or clone the
repository and run `.\install.cmd`.

```powershell
git clone https://github.com/zjxps2007/UnityBridge.git
cd UnityBridge
.\install.cmd
```

If you prefer running the PowerShell script directly, bypass the execution policy
for this process only:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

### 3. Check the connection

Keep the Unity project open, then run:

```powershell
unity-bridge status
unity-bridge instances
unity-bridge call list
```

## Version Pinning

After tags are published, append the tag to the Unity package URL:

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-bridge-connector#v0.1.0
```

## CLI Usage

Installed command:

```powershell
unity-bridge status
unity-bridge instances
unity-bridge call list
```

The same CLI is also available as `unity_bridge`.

Add `--json` when another program or agent should parse the output:

```powershell
unity-bridge --json instances
unity-bridge --json call list
```

Module form without installing:

```powershell
$env:PYTHONPATH='D:\Code\Codex\CP\UnityBridge\src'
python -m unity_bridge status
python -m unity_bridge instances
python -m unity_bridge call list
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
from unity_bridge import UnityClient

client = UnityClient(project=r"D:\UnityProjects\MyGame")
status = client.status()
print(status.state, status.port)

result = client.call("list")
print(result.success, result.message, result.data)
```

## Run tests

```powershell
git clone https://github.com/zjxps2007/UnityBridge.git
cd UnityBridge
python -m pip install -e .
python -m unittest discover -s tests
```

## License

UnityBridge is licensed under the MIT License.

Third-party license notices are listed in `NOTICE.md`.
