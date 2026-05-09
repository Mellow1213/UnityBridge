# UnityBridge

한국어 | [English](README.md)

UnityBridge는
[`youngwoocho02/unity-cli`](https://github.com/youngwoocho02/unity-cli)의
Unity Connector 프로토콜과 호환되는 Python-native 클라이언트와 Unity 패키지입니다.

Python 클라이언트는 `unity-cli` 바이너리를 호출하지 않습니다. 대신 Unity Editor 안에서 실행되는
Connector와 직접 통신합니다.

1. `~/.unity-cli/instances/*.json` heartbeat 파일을 읽습니다.
2. 포트, 프로젝트 경로, 현재 작업 경로, 최신 heartbeat를 기준으로 실행 중인 Unity Editor를 선택합니다.
3. `http://127.0.0.1:{port}/command`로 JSON 요청을 보냅니다.

이 저장소는 `D:\Code\Codex\Agent`와 분리된 독립 프로젝트입니다. Agent에 통합하기 전에
별도로 테스트하고 발전시킬 수 있게 구성했습니다.

## 빠른 시작

### 1. Unity 패키지 설치

Unity Editor에서:

1. `Window > Package Manager`를 엽니다.
2. `+` 버튼을 누릅니다.
3. `Add package from git URL...`을 선택합니다.
4. 아래 URL을 붙여넣습니다.

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-connector
```

Connector는 Unity Editor가 열릴 때 자동으로 시작됩니다. 실행 중에는
`~/.unity-cli/instances/` 아래에 heartbeat 파일을 기록합니다. Python 클라이언트는 이 파일을
읽어 Unity Editor를 발견하고 `http://127.0.0.1:{port}/command`로 명령을 보냅니다.

### 2. Python 클라이언트 설치

```powershell
git clone https://github.com/zjxps2007/UnityBridge.git
cd UnityBridge
python -m pip install -e .
```

### 3. 연결 확인

Unity 프로젝트를 열어둔 상태에서 실행합니다.

```powershell
unity-bridge status
unity-bridge --json instances
unity-bridge --json call list
```

## Unity 패키지 URL

Unity Package Manager에 아래 URL을 넣으면 됩니다.

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-connector
```

나중에 tag를 배포하면 특정 버전으로 고정할 수 있습니다.

```text
https://github.com/zjxps2007/UnityBridge.git?path=unity-connector#v0.1.0
```

## CLI 사용법

설치 후 명령어:

```powershell
unity-bridge status
unity-bridge --json instances
unity-bridge --json call list
```

설치하지 않고 모듈 경로로 실행:

```powershell
$env:PYTHONPATH='D:\Code\Codex\CP\UnityBridge\src'
python -m unity_cli_native status
python -m unity_cli_native --json instances
python -m unity_cli_native --json call list
```

## 명령 예시

UnityBridge는 Unity Connector의 command 이름을 그대로 보냅니다.

```powershell
# Play Mode 진입 후 Unity 확인까지 대기
unity-bridge call manage_editor --params '{"action":"play","wait_for_completion":true}'

# Play Mode 종료
unity-bridge call manage_editor --params '{"action":"stop"}'

# 에셋 새로고침
unity-bridge call refresh_unity --params '{}'

# 콘솔 로그 읽기
unity-bridge call read_console --params '{"count":20,"types":["error","warning","log"]}'

# EditMode 테스트 실행
unity-bridge call run_tests --params '{"mode":"EditMode"}'

# 안전한 Unity 메뉴 실행
unity-bridge call execute_menu_item --params '{"menu_path":"File/Save Project"}'
```

특정 Unity Editor 인스턴스를 선택할 수도 있습니다.

```powershell
unity-bridge --project D:\UnityProjects\MyGame status
unity-bridge --port 8090 status
unity-bridge call --project D:\UnityProjects\MyGame read_console --params '{"count":20}'
```

## Python 사용 예시

```python
from unity_cli_native import UnityClient

client = UnityClient(project=r"D:\UnityProjects\MyGame")
status = client.status()
print(status.state, status.port)

result = client.call("list")
print(result.success, result.message, result.data)
```

## 테스트 실행

```powershell
python -m unittest discover -s tests
```

## 라이선스

UnityBridge는 MIT License로 배포됩니다.

`unity-connector`의 일부는 MIT License로 배포되는
`youngwoocho02/unity-cli` Unity Connector를 기반으로 합니다. 자세한 고지는 `NOTICE.md`를
확인하세요.
