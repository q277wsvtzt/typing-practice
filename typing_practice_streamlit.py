"""
타자 연습기 — Streamlit 버전

설치:
    pip install streamlit streamlit-keyup

실행:
    streamlit run typing_practice_streamlit.py

특징:
- 실시간 키 입력 피드백 (streamlit-keyup)
- 현재 입력해야 할 글자를 앰버 배경 + 펄싱으로 강조
- Enter → 다음 문장 (JS로 버튼 클릭 트리거)
- Backspace는 input 자체에서 자연스럽게 동작
- 3가지 모드 + ortho 키보드 디스플레이
"""

import streamlit as st
import streamlit.components.v1 as components
import random
import time

try:
    from st_keyup import st_keyup
except ImportError:
    from streamlit_keyup import st_keyup


# =========================================================
# Layouts & Mappings
# =========================================================

USER_COLEMAK_LAYOUT = [
    ['q', 'w', 'f', 'p', 'b', 'j', 'l', 'u', 'y', None],
    ['a', 'r', 's', 't', 'g', 'm', 'n', 'e', 'i', 'o'],
    [None, 'x', 'c', 'd', 'v', 'z', 'k', 'h', None, None],
]

QWERTY_LAYOUT = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', None],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm', None, None, None],
]

HOME_BUMPS = {(1, 3), (1, 6)}

# 사용자 커스텀 Colemak (표준 Colemak-DH에서 아래줄만 다름)
QWERTY_TO_USER_COLEMAK = {
    'q':'q','w':'w','e':'f','r':'p','t':'b',
    'y':'j','u':'l','i':'u','o':'y','p':';',
    'a':'a','s':'r','d':'s','f':'t','g':'g',
    'h':'m','j':'n','k':'e','l':'i',';':'o',
    'x':'x','c':'c','v':'d','b':'v',
    'n':'z','m':'k',',':'h',
    'Q':'Q','W':'W','E':'F','R':'P','T':'B',
    'Y':'J','U':'L','I':'U','O':'Y','P':':',
    'A':'A','S':'R','D':'S','F':'T','G':'G',
    'H':'M','J':'N','K':'E','L':'I',':':'O',
    'X':'X','C':'C','V':'D','B':'V',
    'N':'Z','M':'K','<':'H',
}
for _c in "1234567890!@#$%^&*()-_=+[]{}\\|\"'` ~\t\n":
    QWERTY_TO_USER_COLEMAK.setdefault(_c, _c)


# =========================================================
# Sentences
# =========================================================

SENTENCES = [
    # 팬그램
    "the quick brown fox jumps over the lazy dog",
    "pack my box with five dozen liquor jugs",
    "how vexingly quick daft zebras jump",
    "sphinx of black quartz judge my vow",
    "jackdaws love my big sphinx of quartz",
    "the five boxing wizards jump quickly",
    "amazingly few discotheques provide jukeboxes",
    "waltz bad nymph for quick jigs vex",
    # 짧은 워밍업
    "practice makes progress not perfect",
    "small steps every day lead to big results",
    "learning a new layout takes patience and time",
    "focus on accuracy first then speed will follow",
    "typing is a skill built one key at a time",
    "simplicity is the ultimate sophistication",
    "every expert was once a beginner",
    "quality over quantity every single time",
    "slow is smooth and smooth is fast",
    "read more think more write more",
    "keep it simple but not simpler",
    "done is better than perfect",
    # 프로그래밍 격언
    "code is read much more often than it is written",
    "premature optimization is the root of all evil",
    "make it work make it right make it fast",
    "the best error message is the one that never shows up",
    "programs must be written for people to read",
    "simple things should be simple and complex things possible",
    "any fool can write code that a computer can understand",
    "there are only two hard things in computer science",
    "talk is cheap show me the code",
    "debugging is twice as hard as writing the code",
    "first solve the problem then write the code",
    "the most important property of a program is correctness",
    # 중간 격언
    "the best way to predict the future is to create it",
    "every expert was once a beginner who refused to give up",
    "knowledge is power but enthusiasm pulls the switch",
    "success is not final and failure is not fatal",
    "the journey of a thousand miles begins with a single step",
    "what we think we become with every thought and action",
    "imagination is more important than knowledge itself",
    "education is the most powerful weapon you can use",
    "happiness is not ready made it comes from your actions",
    "the only way to do great work is to love what you do",
    "do not wait for opportunity create it yourself",
    # 긴 도전
    "if you want to go fast go alone if you want to go far go together",
    "do not go where the path may lead instead leave a trail behind you",
    "the future belongs to those who believe in the beauty of their dreams",
    "it does not matter how slowly you go as long as you do not stop",
    "you miss one hundred percent of the shots you never take",
    "life is what happens to you while you are busy making other plans",
    "the greatest glory lies not in never falling but in rising every time we fall",
    "success is walking from failure to failure with no loss of enthusiasm",
    # 산문
    "coffee in the morning brings clarity to scattered thoughts",
    "rain falls gently on the quiet streets of the old city",
    "books are the quietest and most constant of friends",
    "music gives soul to the universe and wings to the mind",
    "a cup of tea in the evening calms the restless mind",
    "travel is the only thing you buy that makes you richer",
    "the mountain whispers ancient secrets to those who listen",
    "autumn leaves drift softly through the crisp evening air",
    "stars scatter across the sky like quiet messages from forever",
    "the ocean has a rhythm that heals every tired heart",
    "the garden was full of tomatoes and fresh basil that summer",
    "she walked home through the park under the yellow streetlights",
    "coffee shops on rainy mornings have a peculiar kind of magic",
    "he spent hours drawing maps of imaginary places in his notebook",
    "the old library smelled of dust and forgotten adventures",
    "morning light poured through the window like liquid gold",
    "the river carried leaves and whispers toward the distant sea",
    "silence in the forest speaks louder than any words could",
    "a quiet afternoon with a good book is time well spent",
    "the smell of fresh bread floated down the narrow street",
]


# =========================================================
# Page config
# =========================================================

st.set_page_config(
    page_title="타자 연습기",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>
:root {
    --bg: #0d0c0a;
    --fg: #e8e4d8;
    --dim: #4a4739;
    --muted: #6b6556;
    --accent: #e8a547;
    --error: #c65d5d;
    --key-bg: #1a1815;
    --key-border: #2a2722;
}

.stApp { background: var(--bg); }

h1.brand {
    font-family: 'Fraunces', Georgia, serif;
    font-style: italic;
    font-weight: 400;
    color: var(--fg);
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
h1.brand::before { content: '— '; color: var(--accent); }

/* Target text with character highlighting */
.target-text {
    font-family: 'JetBrains Mono', Menlo, Consolas, monospace;
    font-size: 1.7rem;
    line-height: 2;
    text-align: center;
    padding: 28px 20px;
    background: #12110e;
    border-radius: 10px;
    border: 1px solid var(--key-border);
    margin: 16px 0;
    letter-spacing: 0.02em;
    word-spacing: 0.3em;
}
.target-text span {
    padding: 2px 1px;
    border-radius: 3px;
    transition: color 0.08s;
}
.char-dim { color: var(--dim); }
.char-correct { color: var(--fg); }
.char-incorrect {
    color: var(--error);
    text-decoration: underline;
    text-decoration-thickness: 2px;
    text-underline-offset: 4px;
}
/* Current character — very prominent */
.char-current {
    background: var(--accent);
    color: #0d0c0a !important;
    font-weight: 700;
    padding: 2px 4px;
    animation: pulse 1.2s ease-in-out infinite;
    box-shadow: 0 0 16px rgba(232, 165, 71, 0.5);
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 16px rgba(232, 165, 71, 0.5); }
    50%      { box-shadow: 0 0 24px rgba(232, 165, 71, 0.85); }
}

/* Keyboard */
.kb-container {
    display: flex;
    flex-direction: column;
    gap: 6px;
    align-items: center;
    padding: 20px 0 8px;
}
.kb-row { display: flex; gap: 6px; }
.kb-key {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--key-bg);
    border: 1px solid var(--key-border);
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--muted);
    position: relative;
}
.kb-empty { background: transparent; border-color: transparent; }
.kb-next {
    background: var(--accent) !important;
    color: #0d0c0a !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 20px rgba(232, 165, 71, 0.4);
    font-weight: 700;
    transform: translateY(-2px);
}
.kb-bump::after {
    content: '';
    position: absolute;
    bottom: 5px; left: 50%;
    transform: translateX(-50%);
    width: 10px; height: 2px;
    background: var(--muted);
    border-radius: 1px;
}
.kb-next.kb-bump::after { background: #0d0c0a; }
.kb-space {
    width: 240px;
    height: 32px;
    background: var(--key-bg);
    border: 1px solid var(--key-border);
    border-radius: 6px;
}

/* Streamlit metric styling */
[data-testid="stMetricValue"] {
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 300;
    color: var(--fg);
}
[data-testid="stMetricLabel"] {
    color: var(--muted);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Footer caption */
.footer-note {
    text-align: center;
    color: var(--muted);
    font-size: 0.8rem;
    margin-top: 8px;
}

/* Hide the st_keyup input box completely.
   We capture keystrokes via JS auto-focus instead. */
div.element-container:has(iframe[title*="keyup"]) {
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}
iframe[title*="keyup"] {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 1px !important;
    height: 1px !important;
    opacity: 0 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# Session state
# =========================================================

if 'target' not in st.session_state:
    st.session_state.target = random.choice(SENTENCES)
if 'typed_offset' not in st.session_state:
    st.session_state.typed_offset = 0
if 'advance_flag' not in st.session_state:
    st.session_state.advance_flag = False
if 'reset_flag' not in st.session_state:
    st.session_state.reset_flag = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None


# =========================================================
# Callbacks
#
# 버튼 콜백은 직접 상태 변경하지 않고 플래그만 세팅함.
# 실제 처리는 main flow에서 raw_input을 읽은 후에 함
# (offset 계산에 raw_input 길이가 필요하기 때문).
# =========================================================

def next_sentence():
    st.session_state.advance_flag = True

def reset_sentence():
    st.session_state.reset_flag = True


# =========================================================
# Header
# =========================================================

st.markdown("<h1 class='brand'>typing study</h1>", unsafe_allow_html=True)

mode = st.radio(
    "모드",
    options=['qwerty', 'colemak-sw', 'colemak-hw'],
    format_func=lambda x: {
        'qwerty': 'QWERTY',
        'colemak-sw': 'Colemak · SW',
        'colemak-hw': 'Colemak · HW',
    }[x],
    index=1,
    horizontal=True,
    label_visibility='collapsed',
)


# =========================================================
# Input (real-time via streamlit-keyup)
#
# 핵심: key를 "typing_input"으로 고정해서 컴포넌트가 절대 remount 되지
# 않게 함. 그러면 포커스가 유지되고, 입력창이 화면에 다시 나타나는
# 문제가 없음. 대신 typed_offset으로 "가상 리셋" — 입력은 내부적으로
# 누적되지만 offset 이후 부분만 현재 문장의 타이핑으로 간주.
# =========================================================

raw_input = st_keyup(
    "타이핑",
    key="typing_input",  # 고정 key - 절대 바꾸지 않음
    label_visibility="collapsed",
    placeholder="",
    debounce=20,
) or ""

# Backspace로 offset 이전까지 지운 경우 offset을 따라 내림
if len(raw_input) < st.session_state.typed_offset:
    st.session_state.typed_offset = len(raw_input)

# 버튼 플래그 처리 (콜백에서 raw_input을 참조할 수 없어 여기서 처리)
if st.session_state.advance_flag:
    st.session_state.advance_flag = False
    st.session_state.typed_offset = len(raw_input)
    candidates = [s for s in SENTENCES if s != st.session_state.target]
    st.session_state.target = random.choice(candidates or SENTENCES)
    st.session_state.start_time = None
    st.rerun()

if st.session_state.reset_flag:
    st.session_state.reset_flag = False
    st.session_state.typed_offset = len(raw_input)
    st.session_state.start_time = None
    st.rerun()

# 현재 문장에 해당하는 입력만 추출
current_input = raw_input[st.session_state.typed_offset:]

# 모드별 매핑 적용
if mode == 'colemak-sw':
    typed = ''.join(QWERTY_TO_USER_COLEMAK.get(c, c) for c in current_input)
else:
    typed = current_input

# 첫 키 입력 시 타이머 시작
if typed and st.session_state.start_time is None:
    st.session_state.start_time = time.time()

# 자동 진행: 목표 문장 길이 도달 시 다음 문장으로
if typed and len(typed) >= len(st.session_state.target):
    st.session_state.typed_offset = len(raw_input)
    candidates = [s for s in SENTENCES if s != st.session_state.target]
    st.session_state.target = random.choice(candidates or SENTENCES)
    st.session_state.start_time = None
    st.rerun()


# =========================================================
# Target with color coding
# =========================================================

target = st.session_state.target
html_parts = ['<div class="target-text">']
for i, ch in enumerate(target):
    display_ch = '&nbsp;' if ch == ' ' else ch
    if i < len(typed):
        css = 'char-correct' if typed[i] == ch else 'char-incorrect'
    elif i == len(typed):
        css = 'char-current'
    else:
        css = 'char-dim'
    html_parts.append(f'<span class="{css}">{display_ch}</span>')
html_parts.append('</div>')
st.markdown(''.join(html_parts), unsafe_allow_html=True)


# =========================================================
# Stats
# =========================================================

correct = sum(1 for i, c in enumerate(typed) if i < len(target) and c == target[i])
typed_n = len(typed)
acc = int(correct / typed_n * 100) if typed_n else 100
prog = min(100, int(typed_n / len(target) * 100)) if target else 0
wpm = 0
if st.session_state.start_time and typed_n > 0:
    elapsed = (time.time() - st.session_state.start_time) / 60
    if elapsed > 0:
        wpm = int((correct / 5) / elapsed)

c1, c2, c3 = st.columns(3)
c1.metric("WPM", wpm)
c2.metric("ACCURACY", f"{acc}%")
c3.metric("PROGRESS", f"{prog}%")


# =========================================================
# Buttons
# =========================================================

cb1, cb2, _ = st.columns([1, 1, 2])
cb1.button("다음 문장 →", on_click=next_sentence, use_container_width=True, type="primary")
cb2.button("다시", on_click=reset_sentence, use_container_width=True)


# =========================================================
# Keyboard
# =========================================================

next_char = target[typed_n] if typed_n < len(target) else ''
is_ortho = mode != 'qwerty'
layout = USER_COLEMAK_LAYOUT if is_ortho else QWERTY_LAYOUT
row_offsets = [0, 0, 0] if is_ortho else [0, 22, 44]

kb_html = ['<div class="kb-container">']
for r, row in enumerate(layout):
    kb_html.append(f'<div class="kb-row" style="margin-left: {row_offsets[r]}px;">')
    for c, ch in enumerate(row):
        if ch is None:
            kb_html.append('<div class="kb-key kb-empty"></div>')
        else:
            classes = ['kb-key']
            if next_char and ch == next_char.lower():
                classes.append('kb-next')
            if (r, c) in HOME_BUMPS:
                classes.append('kb-bump')
            kb_html.append(f'<div class="{" ".join(classes)}">{ch.upper()}</div>')
    kb_html.append('</div>')

# Spacebar
space_cls = 'kb-space'
if next_char == ' ':
    space_cls += ' kb-next'
kb_html.append(f'<div class="kb-row"><div class="{space_cls}"></div></div>')
kb_html.append('</div>')

st.markdown(''.join(kb_html), unsafe_allow_html=True)


# =========================================================
# Footer
# =========================================================

footer_text = {
    'qwerty': 'QWERTY · 스태거드 레이아웃',
    'colemak-sw': 'Colemak (SW) · QWERTY 자판을 앱이 Colemak으로 변환 · ortho 디스플레이',
    'colemak-hw': 'Colemak (HW) · OS가 이미 Colemak으로 매핑 · ortho 디스플레이',
}[mode]
st.markdown(f"<div class='footer-note'>{footer_text}</div>", unsafe_allow_html=True)


# =========================================================
# JS: 숨겨진 st_keyup 입력에 자동 포커스
#
# st_keyup은 숨겨놨지만 여전히 keystroke을 받아야 함.
# 페이지 로드 시 · 주기적으로 · 페이지 클릭 시 iframe 내부 input에
# focus를 강제로 주입. streamlit-keyup은 pip 설치 컴포넌트라 Streamlit
# 서버가 같은 origin에서 iframe을 서빙하므로 contentDocument 접근 가능.
# 혹시 cross-origin으로 막히면 iframe.focus()로 폴백.
# =========================================================

components.html("""
<script>
(function() {
    const pwin = window.parent;
    const pdoc = pwin.document;

    const focusInput = () => {
        const iframes = pdoc.querySelectorAll('iframe');
        for (const iframe of iframes) {
            if (!(iframe.title || '').includes('keyup')) continue;
            try {
                const idoc = iframe.contentDocument;
                if (idoc) {
                    const input = idoc.querySelector('input');
                    if (input && idoc.activeElement !== input) {
                        input.focus();
                    }
                }
            } catch (e) {
                try { iframe.focus(); } catch (e2) {}
            }
            return;
        }
    };

    // 초기 포커스 (DOM 로딩 타이밍 차이 대비)
    setTimeout(focusInput, 100);
    setTimeout(focusInput, 400);
    setTimeout(focusInput, 1000);

    // 주기적 재포커스 (rerun 후에도 유지)
    setInterval(focusInput, 400);

    // 페이지 아무 데나 클릭해도 다시 포커스
    pdoc.addEventListener('click', (e) => {
        const tag = (e.target.tagName || '').toUpperCase();
        if (['BUTTON', 'INPUT', 'SELECT', 'TEXTAREA', 'LABEL', 'A'].includes(tag)) return;
        if (e.target.closest('button') || e.target.closest('label') || e.target.closest('a')) return;
        setTimeout(focusInput, 50);
    });
})();
</script>
""", height=0)
