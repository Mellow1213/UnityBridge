# UnityBridge

한국어 | [English](README.md)

UnityBridge는 로컬 HTTP connector를 통해 Unity Editor를 제어하는
Python-native 클라이언트와 Unity 패키지입니다.

Python 클라이언트는 별도의 CLI 바이너리를 호출하지 않습니다. 대신 Unity Editor 안에서 실행되는
connector와 직접 통신합니다.

1. `~/.unity-bridge/instances/*.json` heartbeat 파일을 읽습니다.
2. 포트, 프로젝트 경로, 현재 작업 경로, 최신 heartbeat를 기준으로 실행 중인 Unity Editor를 선택합니다.
3. `http://127.0.0.1:{port}/command`로 JSON 요청을 보냅니다.

이 저장소는 `D:\Code\Codex\Agent`와 분리된 독립 프로젝트입니다. Agent에 통합하기 전에
별도로 테스트하고 발전시킬 수 있게 구성했습니다.

## 빠른 시작

### 1. Unity 패키지 설치

Unity Editor에서 `Window > Package Manager > + > Add package from git URL...`을 열고
아래 URL을 붙여넣습니다.

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-bridge-connector
```

Connector는 Unity Editor가 열릴 때 자동으로 시작됩니다. 실행 중에는
`~/.unity-bridge/instances/` 아래에 heartbeat 파일을 기록합니다. Python 클라이언트는 이 파일을
읽어 Unity Editor를 발견하고 `http://127.0.0.1:{port}/command`로 명령을 보냅니다.

### 권장 Editor 설정

기본적으로 Unity는 창이 포커스를 잃으면 Editor 업데이트를 쓰로틀링할 수 있습니다. UnityBridge는
Unity API 작업을 Editor 메인 스레드에서 디스패치하므로, Editor가 백그라운드에 있으면 CLI 명령
처리가 지연될 수 있습니다.

백그라운드 응답성을 가장 안정적으로 유지하려면 다음처럼 설정하세요.

```text
Edit > Preferences > General > Interaction Mode > No Throttling
```

커넥터도 CLI 요청이 들어올 때마다 PlayerLoop 업데이트를 요청합니다. 그래도 가장 안정적인 응답
시간을 위해 `No Throttling` 설정을 권장합니다.

### 2. Python 클라이언트 설치

```powershell
python -m pip install --upgrade "git+https://github.com/zjxps2007/UnityBridge.git"
```

저장소가 public이면 PowerShell 설치 스크립트를 바로 실행할 수도 있습니다.

```powershell
irm https://raw.githubusercontent.com/zjxps2007/UnityBridge/main/install.ps1 | iex
```

private 저장소에서는 `raw.githubusercontent.com`이 인증 없이 접근되지 않아 `404`가 날 수
있습니다. 이 경우 위의 `pip install` 명령을 쓰거나 저장소를 clone한 뒤 `.\install.cmd`를
실행하세요.

```powershell
git clone https://github.com/zjxps2007/UnityBridge.git
cd UnityBridge
.\install.cmd
```

PowerShell 스크립트를 직접 실행하고 싶다면 현재 실행에만 Execution Policy를 우회할 수 있습니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

### 3. 연결 확인

Unity 프로젝트를 열어둔 상태에서 실행합니다.

```powershell
unity-bridge status
unity-bridge instances
unity-bridge tools
```

## 버전 고정

tag를 배포한 뒤에는 Unity 패키지 URL 뒤에 tag를 붙여 고정할 수 있습니다.

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-bridge-connector#v0.1.0
```

## CLI 사용법

설치 후 명령어:

```powershell
unity-bridge status
unity-bridge instances
unity-bridge tools
```

같은 CLI를 `unity_bridge` 명령어로도 사용할 수 있습니다.

다른 프로그램이나 에이전트가 결과를 파싱해야 할 때만 `--json` 옵션을 붙입니다.

```powershell
unity-bridge --json instances
unity-bridge --json console --count 20
```

설치하지 않고 모듈 경로로 실행:

```powershell
$env:PYTHONPATH='D:\Code\Codex\CP\UnityBridge\src'
python -m unity_bridge status
python -m unity_bridge instances
python -m unity_bridge tools
```

## 지금 사용 가능한 명령어

공통 옵션은 모든 명령어 앞이나 뒤에 붙일 수 있습니다.

```powershell
unity-bridge --project D:\UnityProjects\MyGame status
unity-bridge status --project D:\UnityProjects\MyGame
unity-bridge --port 8090 console --count 20
unity-bridge --json console --count 20
```

| 명령어 | 용도 |
|--------|------|
| `unity-bridge instances` | 발견된 Unity Editor 인스턴스 목록을 출력합니다. |
| `unity-bridge status` | 선택된 Unity Editor 인스턴스 상태를 출력합니다. |
| `unity-bridge tools` | Unity Connector가 제공하는 도구 목록과 파라미터 스키마를 출력합니다. |
| `unity-bridge refresh` | Unity 에셋을 새로고침합니다. |
| `unity-bridge console` | Unity Console 로그를 읽거나 지웁니다. |
| `unity-bridge test` | Unity EditMode/PlayMode 테스트를 실행합니다. |
| `unity-bridge editor` | Play Mode 진입, 종료, 일시정지를 제어합니다. |
| `unity-bridge menu` | Unity 메뉴 아이템을 경로로 실행합니다. |
| `unity-bridge reserialize` | Unity 에셋을 강제로 리시리얼라이즈합니다. |
| `unity-bridge profiler` | Unity Profiler 상태 확인, 활성화, 비활성화, 초기화, hierarchy 호출을 실행합니다. |
| `unity-bridge screenshot` | Scene/Game 뷰 스크린샷을 저장합니다. |
| `unity-bridge exec` | Unity Editor 안에서 임의 C# 코드를 실행합니다. |
| `unity-bridge call` | connector command 이름과 JSON params를 직접 보내는 raw 호출입니다. |
| `unity-bridge wait-ready` | Unity가 ready 상태가 될 때까지 대기합니다. |

### 공통 옵션

| 옵션 | 설명 |
|------|------|
| `--project PATH_OR_TEXT` | 프로젝트 경로 일부로 Unity 인스턴스를 선택합니다. |
| `--port PORT` | 포트 번호로 Unity 인스턴스를 선택합니다. |
| `--timeout-ms MS` | HTTP 요청 타임아웃입니다. 기본값은 `120000`입니다. |
| `--instances-dir PATH` | 기본 `~/.unity-bridge/instances` 대신 다른 heartbeat 폴더를 사용합니다. |
| `--json` | 결과를 JSON으로 출력합니다. 에이전트가 파싱할 때 사용합니다. |

### 명령별 사용법

```powershell
# Unity 인스턴스 확인
unity-bridge instances
unity-bridge status
unity-bridge tools
unity-bridge wait-ready --timeout-sec 300

# 에셋 새로고침
unity-bridge refresh
unity-bridge refresh --mode force
unity-bridge refresh --force
unity-bridge refresh --compile request

# 콘솔 로그
unity-bridge console
unity-bridge console --count 20
unity-bridge console --type error --type warning
unity-bridge console --stacktrace none
unity-bridge console --stacktrace full
unity-bridge console --clear

# Editor 제어
unity-bridge editor play
unity-bridge editor play --wait
unity-bridge editor stop
unity-bridge editor stop --wait
unity-bridge editor pause

# 테스트 실행
unity-bridge test
unity-bridge test --mode EditMode
unity-bridge test --mode PlayMode
unity-bridge test --filter MyTestClass
unity-bridge test --allow-dirty-scenes
unity-bridge test --auto-save-scenes

# Unity 메뉴
unity-bridge menu "File/Save Project"
unity-bridge menu "Assets/Refresh"
unity-bridge menu "Window/General/Console"

# 에셋 리시리얼라이즈
unity-bridge reserialize
unity-bridge reserialize Assets/Prefabs/Player.prefab
unity-bridge reserialize Assets/Scenes/Main.unity Assets/Scenes/Lobby.unity

# Profiler
unity-bridge profiler status
unity-bridge profiler enable
unity-bridge profiler disable
unity-bridge profiler clear
unity-bridge profiler hierarchy

# 스크린샷
unity-bridge screenshot
unity-bridge screenshot --view scene --output-path Screenshots/scene.png
unity-bridge screenshot --view game --width 1280 --height 720

# C# 코드 실행
unity-bridge exec --code "return UnityEditor.EditorApplication.isPlaying;"
unity-bridge exec --code "return UnityEngine.Application.dataPath;"
unity-bridge exec --code-file .\query.cs
unity-bridge exec --code "return Unity.Entities.World.All.Count;" --using Unity.Entities

# Raw connector command 호출
unity-bridge call list
unity-bridge call console --params '{"count":20,"type":"error,warning"}'
unity-bridge call manage_editor --params '{"action":"play","wait_for_completion":true}'
unity-bridge call my_custom_tool --params '{"key":"value"}'
```

`profiler hierarchy`의 `depth`, `root`, `frames` 같은 세부 파라미터나 프로젝트 커스텀 도구의
임의 파라미터는 현재 짧은 CLI 옵션으로 모두 열려 있지는 않습니다. 그런 경우에는
`unity-bridge call <command> --params '{...}'` 형식을 사용하세요.

## 명령 예시

대부분의 작업은 짧은 adapter 명령으로 실행할 수 있습니다.

```powershell
# Play Mode 진입 후 Unity 확인까지 대기
unity-bridge editor play --wait

# Play Mode 종료
unity-bridge editor stop

# 에셋 새로고침
unity-bridge refresh

# 콘솔 로그 읽기
unity-bridge console --count 20 --type error --type warning --type log

# 콘솔 로그 지우기
unity-bridge console --clear

# EditMode 테스트 실행
unity-bridge test --mode EditMode

# Unity 메뉴 실행
unity-bridge menu "File/Save Project"

# connector를 통해 임의 C# 코드 실행
unity-bridge exec --code "return UnityEditor.EditorApplication.isPlaying;"
```

낮은 수준의 connector 접근이 필요하면 `call`을 그대로 사용할 수 있습니다. 이 모드에서는
UnityBridge가 Unity Connector의 command 이름과 params를 직접 보냅니다.

```powershell
# Play Mode 진입 후 Unity 확인까지 대기
unity-bridge call manage_editor --params '{"action":"play","wait_for_completion":true}'

# Play Mode 종료
unity-bridge call manage_editor --params '{"action":"stop"}'

# 에셋 새로고침
unity-bridge call refresh_unity --params '{}'

# 콘솔 로그 읽기
unity-bridge call console --params '{"count":20,"type":"error,warning,log"}'

# EditMode 테스트 실행
unity-bridge call run_tests --params '{"mode":"EditMode"}'

# Unity 메뉴 실행
unity-bridge call menu --params '{"menu_path":"File/Save Project"}'
```

특정 Unity Editor 인스턴스를 선택할 수도 있습니다.

```powershell
unity-bridge --project D:\UnityProjects\MyGame status
unity-bridge --port 8090 status
unity-bridge --project D:\UnityProjects\MyGame console --count 20 --type error
```

## Python 사용 예시

```python
from unity_bridge import UnityBridgeAdapter

bridge = UnityBridgeAdapter(project=r"D:\UnityProjects\MyGame")

bridge.refresh_assets()
logs = bridge.read_console(count=50, types=["error", "warning", "log"])
tests = bridge.run_tests(mode="EditMode")
```

adapter는 의도적으로 얇은 계층입니다. 쓰기 쉬운 Python 메서드를 connector command로 매핑하지만,
allowlist나 denylist 같은 정책 계층은 추가하지 않습니다. connector params를 정확히 지정해야 하면
`UnityClient`로 raw 호출을 사용할 수 있습니다.

```python
from unity_bridge import UnityClient

client = UnityClient(project=r"D:\UnityProjects\MyGame")
status = client.status()
print(status.state, status.port)

result = client.call("console", {"count": 20, "type": "error,warning"})
print(result.success, result.message, result.data)
```

## 테스트 실행

```powershell
git clone https://github.com/zjxps2007/UnityBridge.git
cd UnityBridge
python -m pip install -e .
python -m unittest discover -s tests
```

## 라이선스

UnityBridge는 MIT License로 배포됩니다.

제3자 라이선스 고지는 `NOTICE.md`를 확인하세요.
