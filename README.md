# 타자 연습기 — Streamlit Cloud 배포 가이드

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run typing_practice_streamlit.py
```

## Streamlit Community Cloud 배포

### 1. GitHub 레포지토리 준비

레포지토리 루트에 아래 두 파일이 있어야 함:

```
my-typing-app/
├── typing_practice_streamlit.py
└── requirements.txt
```

```bash
# 이미 있는 로컬 폴더에서
git init
git add typing_practice_streamlit.py requirements.txt
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

GitHub Student Pack 이미 활성화돼 있으니 private repo로 올려도 됨.

### 2. Streamlit Cloud 연결

1. https://share.streamlit.io 접속 → GitHub 로그인
2. "Create app" 클릭
3. Repository / Branch / Main file path 선택
   - Main file path: `typing_practice_streamlit.py`
4. "Deploy!" 클릭

처음 배포는 2–3분 걸림. 빌드 로그에서 `streamlit-keyup` 설치 확인.

### 3. 배포 URL

`https://<app-name>-<hash>.streamlit.app` 형태의 URL이 발급됨.

URL은 앱 설정에서 커스터마이즈 가능: `https://typing-practice.streamlit.app` 같은 식.

## 배포 환경에서의 동작 차이

### 동작하는 기능
- 실시간 글자별 색상 피드백
- 현재 글자 하이라이트 (펄싱)
- 키보드 다음 키 표시
- WPM · 정확도 · 진행률
- 모드 전환 (QWERTY / Colemak SW / HW)
- **자동 진행**: 문장 끝까지 치면 다음 문장으로 자동 넘어감
- "다음 문장" 버튼, "다시" 버튼
- Backspace

### 제한 사항
- **Enter 키로 다음 문장 기능은 불안정할 수 있음**  
  `streamlit-keyup` 컴포넌트가 iframe에서 동작하는데, 배포 환경에서는 cross-origin 정책 때문에 JS로 iframe 이벤트를 가로채는 게 차단됨.  
  로컬에서는 동작, 배포에서는 안 될 수 있음.  
  대안: 문장 끝까지 치면 **자동 진행**되므로 대부분의 경우 Enter 불필요. 중간 스킵은 "다음 문장" 버튼.

### 성능
- 매 키스트로크마다 Streamlit 서버로 왕복 → 로컬 대비 체감 latency 있음
- 한국에서 사용 시 Streamlit Cloud 서버(미국) 까지의 RTT가 50–150ms 추가됨
- WPM 60+로 타이핑할 때는 살짝 버벅일 수 있음 (로컬은 문제없음)

## 문제 해결

### 앱이 `ModuleNotFoundError: streamlit_keyup` 에러로 실패
`requirements.txt` 누락. 루트에 있는지 확인.

### 키 하이라이트가 안 뜨거나 CSS가 깨짐
캐시 문제. Streamlit Cloud 우측 상단 "Rerun" 또는 "Clear cache" 시도.

### 앱이 자는 문제 (free tier)
Streamlit Cloud 무료 플랜은 일정 시간 트래픽 없으면 앱이 sleep 상태가 됨.  
첫 접속 시 재기동에 10–20초 걸림. 발표 전에 한 번 접속해서 깨워두면 됨.

### 앱 URL이 공개되는 게 걱정되면
앱 설정에서 "Viewer access" → "Only specific people" 으로 Google 계정 기반 제한 가능.
