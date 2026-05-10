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

### Recommended Editor setting

By default, Unity can throttle Editor updates when the window is not focused.
UnityBridge dispatches Unity API work on the Editor main thread, so CLI command
handling may be delayed while the Editor is in the background.

For the most reliable background responsiveness, set:

```text
Edit > Preferences > General > Interaction Mode > No Throttling
```

The connector also requests PlayerLoop updates whenever a CLI request arrives,
but `No Throttling` is still recommended for the most stable response times.

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
unity-bridge tools
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
unity-bridge tools
```

The same CLI is also available as `unity_bridge`.

Add `--json` when another program or agent should parse the output:

```powershell
unity-bridge --json instances
unity-bridge --json console --count 20
```

Module form without installing:

```powershell
$env:PYTHONPATH='D:\Code\Codex\CP\UnityBridge\src'
python -m unity_bridge status
python -m unity_bridge instances
python -m unity_bridge tools
```

## Available Commands

Common options can be placed before or after the subcommand.

```powershell
unity-bridge --project D:\UnityProjects\MyGame status
unity-bridge status --project D:\UnityProjects\MyGame
unity-bridge --port 8090 console --count 20
unity-bridge --json console --count 20
```

| Command | Purpose |
|---------|---------|
| `unity-bridge instances` | Print discovered Unity Editor instances. |
| `unity-bridge status` | Print the selected Unity Editor instance status. |
| `unity-bridge tools` | Print Unity Connector tools and parameter schemas. |
| `unity-bridge refresh` | Refresh Unity assets. |
| `unity-bridge console` | Read or clear Unity Console logs. |
| `unity-bridge test` | Run Unity EditMode or PlayMode tests. |
| `unity-bridge editor` | Enter, stop, or pause Play Mode. |
| `unity-bridge menu` | Execute a Unity menu item by path. |
| `unity-bridge reserialize` | Force reserialize Unity assets. |
| `unity-bridge profiler` | Run Unity Profiler status, enable, disable, clear, or hierarchy calls. |
| `unity-bridge screenshot` | Save a Scene/Game view screenshot. |
| `unity-bridge exec` | Execute arbitrary C# code inside the Unity Editor. |
| `unity-bridge call` | Send a raw connector command name and JSON params. |
| `unity-bridge wait-ready` | Wait until Unity reaches the ready state. |
| `unity-bridge <tool-name>` | Treat unknown command names as connector/custom tool names and call them directly. |

### Common Options

| Option | Description |
|--------|-------------|
| `--project PATH_OR_TEXT` | Select a Unity instance by project path substring. |
| `--port PORT` | Select a Unity instance by port. |
| `--timeout-ms MS` | HTTP request timeout. Default: `120000`. |
| `--instances-dir PATH` | Use a heartbeat directory other than `~/.unity-bridge/instances`. |
| `--json` | Print JSON output for agents or other programs. |

### Command Usage

```powershell
# Unity instances
unity-bridge instances
unity-bridge status
unity-bridge tools
unity-bridge wait-ready --timeout-sec 300

# Asset refresh
unity-bridge refresh
unity-bridge refresh --mode force
unity-bridge refresh --force
unity-bridge refresh --compile request

# Console logs
unity-bridge console
unity-bridge console --count 20
unity-bridge console --type error --type warning
unity-bridge console --stacktrace none
unity-bridge console --stacktrace full
unity-bridge console --clear

# Editor control
unity-bridge editor play
unity-bridge editor play --wait
unity-bridge editor stop
unity-bridge editor stop --wait
unity-bridge editor pause

# Tests
unity-bridge test
unity-bridge test --mode EditMode
unity-bridge test --mode PlayMode
unity-bridge test --filter MyTestClass
unity-bridge test --allow-dirty-scenes
unity-bridge test --auto-save-scenes

# Unity menu
unity-bridge menu "File/Save Project"
unity-bridge menu "Assets/Refresh"
unity-bridge menu "Window/General/Console"

# Asset reserialization
unity-bridge reserialize
unity-bridge reserialize Assets/Prefabs/Player.prefab
unity-bridge reserialize Assets/Scenes/Main.unity Assets/Scenes/Lobby.unity

# Profiler
unity-bridge profiler status
unity-bridge profiler enable
unity-bridge profiler disable
unity-bridge profiler clear
unity-bridge profiler hierarchy

# Screenshots
unity-bridge screenshot
unity-bridge screenshot --view scene --output-path Screenshots/scene.png
unity-bridge screenshot --view game --width 1280 --height 720

# C# execution
unity-bridge exec --code "return UnityEditor.EditorApplication.isPlaying;"
unity-bridge exec --code "return UnityEngine.Application.dataPath;"
unity-bridge exec --code-file .\query.cs
unity-bridge exec --code "return Unity.Entities.World.All.Count;" --using Unity.Entities

# Raw connector command calls
unity-bridge list
unity-bridge call list
unity-bridge call console --params '{"count":20,"type":"error,warning"}'
unity-bridge call manage_editor --params '{"action":"play","wait_for_completion":true}'
unity-bridge call my_custom_tool --params '{"key":"value"}'

# Direct custom tool calls
unity-bridge spawn --x 1 --y 0 --z 5 --prefab Enemy
unity-bridge spawn --params '{"x":1,"y":0,"z":5,"prefab":"Enemy"}'
unity-bridge my_custom_tool --key value --enabled
unity-bridge my_custom_tool --no-enabled
unity-bridge my_custom_tool first second
```

Unknown command names are sent directly as connector commands. Flags such as
`--x 1` become params like `{"x": 1}`, and `--my-value` becomes `my_value`.
Flags without values are sent as `true`; `--no-name` is sent as `false`.
Plain positional arguments are sent in an `args` array.

Reserved names such as `profiler`, `console`, and `test` are handled by
UnityBridge's built-in CLI first. If a built-in command needs detailed
parameters that are not exposed as short flags yet, use
`unity-bridge call <command> --params '{...}'`.

## Command Examples

Most workflows can use the short adapter commands:

```powershell
# Enter play mode and wait until Unity confirms it.
unity-bridge editor play --wait

# Stop play mode.
unity-bridge editor stop

# Refresh assets.
unity-bridge refresh

# Read console logs.
unity-bridge console --count 20 --type error --type warning --type log

# Clear console logs.
unity-bridge console --clear

# Run EditMode tests.
unity-bridge test --mode EditMode

# Execute a Unity menu item.
unity-bridge menu "File/Save Project"

# Execute arbitrary C# code through the connector.
unity-bridge exec --code "return UnityEditor.EditorApplication.isPlaying;"
```

Raw connector access is still available through `call`. In that mode,
UnityBridge sends the Unity Connector command name and params directly.

```powershell
# Enter play mode and wait until Unity confirms it.
unity-bridge call manage_editor --params '{"action":"play","wait_for_completion":true}'

# Stop play mode.
unity-bridge call manage_editor --params '{"action":"stop"}'

# Refresh assets.
unity-bridge call refresh_unity --params '{}'

# Read console logs.
unity-bridge call console --params '{"count":20,"type":"error,warning,log"}'

# Run EditMode tests.
unity-bridge call run_tests --params '{"mode":"EditMode"}'

# Execute a Unity menu item.
unity-bridge call menu --params '{"menu_path":"File/Save Project"}'
```

Select a specific Unity Editor instance:

```powershell
unity-bridge --project D:\UnityProjects\MyGame status
unity-bridge --port 8090 status
unity-bridge --project D:\UnityProjects\MyGame console --count 20 --type error
```

## Python examples

```python
from unity_bridge import UnityBridgeAdapter

bridge = UnityBridgeAdapter(project=r"D:\UnityProjects\MyGame")

bridge.refresh_assets()
logs = bridge.read_console(count=50, types=["error", "warning", "log"])
tests = bridge.run_tests(mode="EditMode")
```

The adapter is intentionally thin. It maps friendly Python methods to connector
commands, but it does not add an allowlist or denylist policy layer. Raw access
is available through `UnityClient` when you need exact connector params:

```python
from unity_bridge import UnityClient

client = UnityClient(project=r"D:\UnityProjects\MyGame")
status = client.status()
print(status.state, status.port)

result = client.call("console", {"count": 20, "type": "error,warning"})
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
