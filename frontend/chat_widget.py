"""Hira chat bubble.

Streamlit does not run <script> tags or inline event handlers that come from
st.markdown(..., unsafe_allow_html=True), so the widget is built by a tiny
script inside a zero-height components.html iframe that attaches the bubble to
the parent page. The backend URL comes from API_BASE_URL (st.secrets["API_URL"]),
and all chat text is rendered as DOM text nodes (never innerHTML), so model
output can not inject HTML.
"""
import json

import streamlit.components.v1 as components

_CSS = r""".chat-bubble-wrap { position: fixed; bottom: 24px; right: 24px; z-index: 9999; }

.bubble-btn {
    width: 62px; height: 62px; border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #1e1040, #0d0820);
    border: 1.5px solid rgba(139,92,246,0.5);
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 20px rgba(124,58,237,0.4), 0 0 40px rgba(124,58,237,0.15);
    transition: all 0.3s; position: relative;
}
.bubble-btn:hover { box-shadow: 0 0 30px rgba(124,58,237,0.7); transform: scale(1.05); }

.orbital-container { width: 62px; height: 62px; position: relative; display: flex; align-items: center; justify-content: center; }
.ai-core { width: 22px; height: 22px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #a78bfa, #6d28d9); box-shadow: 0 0 12px rgba(167,139,250,0.8); position: absolute; z-index: 3; animation: aiCorePulse 2s ease-in-out infinite; }
@keyframes aiCorePulse { 0%,100%{box-shadow:0 0 12px rgba(167,139,250,0.8);transform:scale(1)} 50%{box-shadow:0 0 20px rgba(167,139,250,1);transform:scale(1.1)} }

.ai-ring { position: absolute; border-radius: 50%; border: 1.5px solid transparent; }
.ai-ring-1 { width: 46px; height: 46px; border-color: rgba(139,92,246,0.7) transparent rgba(139,92,246,0.7) transparent; animation: aiSpin1 2s linear infinite; }
.ai-ring-2 { width: 58px; height: 20px; border-color: rgba(59,130,246,0.6) transparent; animation: aiSpin2 3s linear infinite reverse; transform: rotateX(70deg); }
.ai-ring-3 { width: 54px; height: 54px; border-color: transparent rgba(192,132,252,0.5) transparent rgba(192,132,252,0.5); animation: aiSpin3 4s linear infinite; transform: rotate(45deg); }
.ai-dot { width: 5px; height: 5px; border-radius: 50%; position: absolute; }
.ai-dot-1 { background: #a78bfa; box-shadow: 0 0 6px rgba(167,139,250,1); animation: aiOrbit1 2s linear infinite; }
.ai-dot-2 { background: #60a5fa; box-shadow: 0 0 6px rgba(96,165,250,1); animation: aiOrbit2 3s linear infinite reverse; }

@keyframes aiSpin1 { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
@keyframes aiSpin2 { from{transform:rotateX(70deg) rotate(0deg)} to{transform:rotateX(70deg) rotate(360deg)} }
@keyframes aiSpin3 { from{transform:rotate(45deg)} to{transform:rotate(405deg)} }
@keyframes aiOrbit1 { from{transform:rotate(0deg) translateX(23px) rotate(0deg)} to{transform:rotate(360deg) translateX(23px) rotate(-360deg)} }
@keyframes aiOrbit2 { from{transform:rotate(0deg) translateX(27px) rotate(0deg)} to{transform:rotate(360deg) translateX(27px) rotate(-360deg)} }

.ai-notif { position: absolute; top: 2px; right: 2px; width: 13px; height: 13px; background: #10b981; border-radius: 50%; border: 2px solid #000510; animation: aiNotif 2s infinite; z-index: 10; }
@keyframes aiNotif { 0%,100%{transform:scale(1)} 50%{transform:scale(1.4)} }

.ai-chat-window {
    position: fixed; bottom: 96px; right: 24px;
    width: 360px; height: 520px;
    background: rgba(4,6,22,0.97);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 20px; display: flex; flex-direction: column;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6), 0 0 40px rgba(139,92,246,0.15);
    transform-origin: bottom right;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
    z-index: 9998;
}
.ai-chat-window.ai-hidden { transform: scale(0.8); opacity: 0; pointer-events: none; }

.ai-chat-header {
    padding: 14px 16px;
    background: rgba(139,92,246,0.1);
    border-bottom: 1px solid rgba(139,92,246,0.2);
    display: flex; align-items: center; gap: 12px; flex-shrink: 0;
}
.ai-header-orbital { width: 38px; height: 38px; position: relative; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ai-header-core { width: 14px; height: 14px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #a78bfa, #6d28d9); box-shadow: 0 0 8px rgba(167,139,250,0.8); position: absolute; z-index: 2; animation: aiCorePulse 2s ease-in-out infinite; }
.ai-header-ring { position: absolute; border-radius: 50%; border: 1px solid transparent; }
.ahr1 { width: 28px; height: 28px; border-color: rgba(139,92,246,0.6) transparent rgba(139,92,246,0.6) transparent; animation: aiSpin1 2s linear infinite; }
.ahr2 { width: 34px; height: 14px; border-color: rgba(59,130,246,0.5) transparent; animation: aiSpin2 3s linear infinite reverse; transform: rotateX(70deg); }

.ai-header-name { font-size: 14px; font-weight: 700; color: #e2e8f0; }
.ai-header-status { font-size: 11px; color: #10b981; display: flex; align-items: center; gap: 4px; margin-top: 2px; }
.ai-status-dot { width: 6px; height: 6px; background: #10b981; border-radius: 50%; animation: aiNotif 2s infinite; }
.ai-close-btn { background: none; border: none; cursor: pointer; color: rgba(148,163,184,0.6); font-size: 16px; padding: 6px; border-radius: 8px; margin-left: auto; }
.ai-close-btn:hover { color: #e2e8f0; background: rgba(255,255,255,0.08); }

.ai-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.ai-messages::-webkit-scrollbar { width: 4px; }
.ai-messages::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.3); border-radius: 2px; }

.ai-msg { display: flex; gap: 8px; align-items: flex-end; }
.ai-msg.ai-user { flex-direction: row-reverse; }
.ai-avatar { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; background: linear-gradient(135deg, #7c3aed, #4f46e5); }
.ai-avatar.ai-uav { background: rgba(59,130,246,0.25); border: 1px solid rgba(59,130,246,0.4); }
.ai-bubble { max-width: 78%; padding: 10px 14px; border-radius: 16px; font-size: 13px; line-height: 1.6; }
.ai-bubble.ai-bot { background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.2); color: #e2e8f0; border-bottom-left-radius: 4px; }
.ai-bubble.ai-usr { background: linear-gradient(135deg, rgba(124,58,237,0.3), rgba(79,70,229,0.3)); border: 1px solid rgba(139,92,246,0.35); color: #e2e8f0; border-bottom-right-radius: 4px; }

.ai-typing { display: flex; gap: 4px; align-items: center; padding: 12px 14px; }
.ai-typing span { width: 7px; height: 7px; background: rgba(139,92,246,0.6); border-radius: 50%; animation: aiBounce 1.4s infinite; }
.ai-typing span:nth-child(2) { animation-delay: 0.2s; }
.ai-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes aiBounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-8px)} }

.ai-quick { display: flex; flex-wrap: wrap; gap: 6px; padding: 0 16px 12px; flex-shrink: 0; }
.ai-qbtn { padding: 5px 12px; background: rgba(139,92,246,0.08); border: 1px solid rgba(139,92,246,0.25); border-radius: 999px; color: #a78bfa; font-size: 11px; cursor: pointer; }
.ai-qbtn:hover { background: rgba(139,92,246,0.18); }

.ai-input-area { padding: 12px 14px; border-top: 1px solid rgba(139,92,246,0.15); display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.ai-input { flex: 1; padding: 10px 14px; background: rgba(139,92,246,0.06); border: 1px solid rgba(139,92,246,0.2); border-radius: 12px; color: #e2e8f0; font-size: 13px; outline: none; resize: none; font-family: inherit; }
.ai-input:focus { border-color: rgba(139,92,246,0.5); }
.ai-input::placeholder { color: rgba(100,116,139,0.6); }
.ai-send { width: 38px; height: 38px; background: linear-gradient(135deg, #7c3aed, #4f46e5); border: none; border-radius: 10px; cursor: pointer; color: white; font-size: 16px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.ai-send:hover { transform: scale(1.05); }"""

_MARKUP = r"""<div class="chat-bubble-wrap">
    <button class="bubble-btn" id="hiraBubble" aria-label="Open chat">
        <div class="orbital-container">
            <div class="ai-ring ai-ring-1"></div>
            <div class="ai-ring ai-ring-2"></div>
            <div class="ai-ring ai-ring-3"></div>
            <div class="ai-dot ai-dot-1"></div>
            <div class="ai-dot ai-dot-2"></div>
            <div class="ai-core"></div>
        </div>
        <div class="ai-notif" id="aiNotifDot"></div>
    </button>
</div>

<div class="ai-chat-window ai-hidden" id="aiChatWindow">
    <div class="ai-chat-header">
        <div class="ai-header-orbital">
            <div class="ai-header-ring ahr1"></div>
            <div class="ai-header-ring ahr2"></div>
            <div class="ai-header-core"></div>
        </div>
        <div style="flex:1">
            <div class="ai-header-name">Hira — AI Assistant</div>
            <div class="ai-header-status"><div class="ai-status-dot"></div> Online · Powered by AI</div>
        </div>
        <button class="ai-close-btn" id="hiraClose" aria-label="Close chat">✕</button>
    </div>

    <div class="ai-messages" id="aiMessages">
        <div class="ai-msg">
            <div class="ai-avatar">🤖</div>
            <div class="ai-bubble ai-bot">
                👋 Hi! I'm <strong>Hira</strong>, your AI hiring assistant.<br><br>
                Ask me anything — resume tips, job matching, scoring, interview advice, or anything else!
            </div>
        </div>
    </div>

    <div class="ai-quick" id="aiQuickReplies">
        <button class="ai-qbtn" data-q="How does AI scoring work?">How scoring works?</button>
        <button class="ai-qbtn" data-q="Give me resume tips">Resume tips</button>
        <button class="ai-qbtn" data-q="How do I apply for jobs?">How to apply?</button>
        <button class="ai-qbtn" data-q="What is fraud detection?">Fraud detection</button>
    </div>

    <div class="ai-input-area">
        <textarea class="ai-input" id="aiChatInput" placeholder="Ask me anything..." rows="1"></textarea>
        <button class="ai-send" id="hiraSend" aria-label="Send">➤</button>
    </div>
</div>"""

_JS = r"""(function () {
  var API = __API__;
  var CSS = __CSS__;
  var MARKUP = __MARKUP__;

  var P, doc;
  try { P = window.parent; doc = P.document; void doc.body; } catch (e) { return; }

  // This iframe only hosts the script - keep its slot invisible.
  try {
    var frame = window.frameElement;
    var holder = frame.closest('[data-testid="stElementContainer"]') || frame.parentElement;
    holder.style.display = 'none';
  } catch (e) {}

  // Streamlit may reload this iframe on reruns: rebuild cleanly each time.
  ['hira-root', 'hira-style'].forEach(function (id) {
    var old = doc.getElementById(id); if (old) old.remove();
  });
  var state = P.__hira = P.__hira || { open: false, history: [], log: [] };

  var style = doc.createElement('style'); style.id = 'hira-style'; style.textContent = CSS;
  doc.head.appendChild(style);
  var root = doc.createElement('div'); root.id = 'hira-root'; root.innerHTML = MARKUP;
  doc.body.appendChild(root);

  function $(id) { return doc.getElementById(id); }
  var win = $('aiChatWindow'), msgs = $('aiMessages'), input = $('aiChatInput'),
      quick = $('aiQuickReplies'), dot = $('aiNotifDot');
  var busy = false;

  function setOpen(v) {
    state.open = v;
    win.classList.toggle('ai-hidden', !v);
    dot.style.display = v ? 'none' : 'block';
    if (v) input.focus();
  }

  // Safe rich text: only text nodes, <br> and <strong> are ever created.
  function renderRich(el, text) {
    String(text).split('\n').forEach(function (line, i) {
      if (i) el.appendChild(doc.createElement('br'));
      line.split(/\*\*(.+?)\*\*/g).forEach(function (part, j) {
        if (!part) return;
        if (j % 2) { var s = doc.createElement('strong'); s.textContent = part; el.appendChild(s); }
        else { el.appendChild(doc.createTextNode(part)); }
      });
    });
  }

  function addMessage(text, isUser) {
    var wrap = doc.createElement('div'); wrap.className = 'ai-msg' + (isUser ? ' ai-user' : '');
    var av = doc.createElement('div'); av.className = 'ai-avatar' + (isUser ? ' ai-uav' : '');
    av.textContent = isUser ? '\uD83D\uDC64' : '\uD83E\uDD16';
    var bubble = doc.createElement('div'); bubble.className = 'ai-bubble ' + (isUser ? 'ai-usr' : 'ai-bot');
    renderRich(bubble, text);
    wrap.appendChild(av); wrap.appendChild(bubble); msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function addTyping() {
    var wrap = doc.createElement('div'); wrap.className = 'ai-msg'; wrap.id = 'aiTyping';
    wrap.innerHTML = '<div class="ai-avatar">\uD83E\uDD16</div><div class="ai-bubble ai-bot">' +
      '<div class="ai-typing"><span></span><span></span><span></span></div></div>';
    msgs.appendChild(wrap); msgs.scrollTop = msgs.scrollHeight;
    return wrap;
  }

  async function ask(message) {
    state.history.push({ role: 'user', content: message });
    try {
      var res = await P.fetch(API + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, history: state.history.slice(0, -1).slice(-10) })
      });
      var data = await res.json().catch(function () { return {}; });
      if (!res.ok || typeof data.reply !== 'string') {
        state.history.pop();
        return (typeof data.detail === 'string' && data.detail) ||
               "Sorry, I'm having trouble right now. Please try again!";
      }
      state.history.push({ role: 'assistant', content: data.reply });
      return data.reply;
    } catch (e) {
      state.history.pop();
      return "Sorry, I'm having trouble connecting. Please try again!";
    }
  }

  async function send(text) {
    text = (text || '').trim();
    if (!text || busy) return;
    busy = true;
    addMessage(text, true); state.log.push({ u: true, t: text });
    input.value = ''; input.style.height = 'auto'; quick.style.display = 'none';
    var typing = addTyping();
    var reply = await ask(text);
    typing.remove();
    addMessage(reply, false); state.log.push({ u: false, t: reply });
    state.log = state.log.slice(-50);
    busy = false;
  }

  $('hiraBubble').addEventListener('click', function () { setOpen(!state.open); });
  $('hiraClose').addEventListener('click', function () { setOpen(false); });
  $('hiraSend').addEventListener('click', function () { send(input.value); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input.value); }
  });
  input.addEventListener('input', function () {
    input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 80) + 'px';
  });
  Array.prototype.forEach.call(root.querySelectorAll('.ai-qbtn'), function (b) {
    b.addEventListener('click', function () { send(b.getAttribute('data-q')); });
  });

  // restore the conversation after a reload of this helper iframe
  state.log.forEach(function (m) { addMessage(m.t, m.u); });
  if (state.log.length) quick.style.display = 'none';
  setOpen(state.open);
})();"""


def build_html(api_url: str) -> str:
    script = (
        _JS.replace("__API__", json.dumps(api_url.rstrip("/")))
        .replace("__CSS__", json.dumps(_CSS))
        .replace("__MARKUP__", json.dumps(_MARKUP))
        .replace("</", "<\\/")  # a payload must never be able to close the <script> tag
    )
    return "<script>" + script + "</script>"


def render(api_url: str) -> None:
    components.html(build_html(api_url), height=0)
