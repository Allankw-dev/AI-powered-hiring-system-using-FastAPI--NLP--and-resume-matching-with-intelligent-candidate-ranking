const { JSDOM } = require('jsdom');
const fs = require('fs');
const script = fs.readFileSync(__dirname + '/widget.generated.js', 'utf8');
let failures = 0;
const ok = (c, m) => { console.log((c ? 'PASS  ' : 'FAIL  ') + m); if (!c) failures++; };

function boot(parentDom) {
  const iframe = parentDom.window.document.createElement('iframe');
  parentDom.window.document.getElementById('slot').appendChild(iframe);
  iframe.contentWindow.eval(script);   // run the widget exactly as Streamlit's iframe would
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const parent = new JSDOM('<!doctype html><html><head></head><body><div data-testid="stElementContainer" id="slot"></div></body></html>', { pretendToBeVisual: true, runScripts: 'outside-only' });
  const calls = [];
  let mode = 'ok';
  parent.window.fetch = async (url, opts) => {
    calls.push({ url, body: JSON.parse(opts.body), method: opts.method });
    if (mode === 'net') throw new Error('offline');
    if (mode === '429') return { ok: false, json: async () => ({ detail: "Hira has reached today's chat limit." }) };
    return { ok: true, json: async () => ({ reply: 'Hello **friend**!\nLine two <img src=x onerror=alert(1)> <script>alert(2)</script>' }) };
  };
  const d = parent.window.document;
  boot(parent);

  ok(!!d.getElementById('hira-root') && !!d.getElementById('hira-style'), 'widget + styles attached to the PARENT page');
  ok(d.getElementById('slot').style.display === 'none', 'helper iframe slot is hidden');
  ok(d.getElementById('aiChatWindow').classList.contains('ai-hidden'), 'chat starts closed');

  d.getElementById('hiraBubble').click();
  ok(!d.getElementById('aiChatWindow').classList.contains('ai-hidden'), 'bubble click opens the window');
  d.getElementById('hiraClose').click();
  ok(d.getElementById('aiChatWindow').classList.contains('ai-hidden'), 'close button closes it');
  d.getElementById('hiraBubble').click();

  const input = d.getElementById('aiChatInput');
  input.value = 'hi <b>there</b><script>alert(0)</script>';
  d.getElementById('hiraSend').click();
  await sleep(50);
  ok(calls.length === 1 && calls[0].url === 'https://api.example.com/chat' && calls[0].method === 'POST', 'POSTs to <API_URL>/chat (trailing slash handled)');
  ok(calls[0].body.message.startsWith('hi <b>there') && Array.isArray(calls[0].body.history), 'sends message + history array');

  const msgs = d.getElementById('aiMessages');
  ok(msgs.querySelectorAll('script, img, b').length === 0, 'no <script>/<img>/<b> elements created from user OR bot text (XSS-safe)');
  ok(msgs.textContent.includes('<script>alert(2)</script>') && msgs.textContent.includes('<img src=x onerror=alert(1)>'), 'dangerous text is shown literally as text');
  ok(msgs.querySelectorAll('strong').length === 2, '**bold** renders as <strong> (greeting + reply)');
  ok(d.getElementById('aiTyping') === null, 'typing indicator removed after reply');
  ok(d.getElementById('aiQuickReplies').style.display === 'none', 'quick replies hidden after first message');

  // 2nd turn includes history; Enter key sends; Shift+Enter does not
  input.value = 'second'; 
  input.dispatchEvent(new parent.window.KeyboardEvent('keydown', { key: 'Enter', shiftKey: true, bubbles: true }));
  await sleep(30); ok(calls.length === 1, 'Shift+Enter does not send');
  input.dispatchEvent(new parent.window.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
  await sleep(50);
  ok(calls.length === 2 && calls[1].body.history.length === 2 && calls[1].body.history[0].role === 'user' && calls[1].body.history[1].role === 'assistant', 'Enter sends; history = [user, assistant]');

  // server error detail (e.g. 429) is shown, and failed turn is not kept in history
  mode = '429'; input.value = 'third'; d.getElementById('hiraSend').click(); await sleep(50);
  ok(msgs.textContent.includes("reached today's chat limit"), 'server error detail shown to the user');
  mode = 'ok'; input.value = 'fourth'; d.getElementById('hiraSend').click(); await sleep(50);
  ok(calls[3].body.history.length === 4, 'failed turn was not left in the history');

  mode = 'net'; input.value = 'fifth'; d.getElementById('hiraSend').click(); await sleep(50);
  ok(msgs.textContent.includes('trouble connecting'), 'network failure -> friendly message');
  mode = 'ok';

  // quick reply button
  // (reset UI by simulating the helper iframe reloading: Streamlit rerun)
  const before = d.getElementById('aiMessages').children.length;
  boot(parent);
  ok(d.querySelectorAll('#hira-root').length === 1 && d.querySelectorAll('#hira-style').length === 1, 'reload does not duplicate the widget');
  ok(d.getElementById('aiMessages').children.length >= before - 1, 'conversation restored after iframe reload');
  ok(!d.getElementById('aiChatWindow').classList.contains('ai-hidden'), 'open/closed state restored');
  const input2 = d.getElementById('aiChatInput');
  input2.value = 'after reload'; d.getElementById('hiraSend').click(); await sleep(50);
  ok(calls[calls.length - 1].body.message === 'after reload', 'still works after reload (fresh listeners)');

  // quick-reply button on a brand-new session
  const p2 = new JSDOM('<!doctype html><html><head></head><body><div id="slot"></div></body></html>', { pretendToBeVisual: true, runScripts: 'outside-only' });
  let q = null; p2.window.fetch = async (u, o) => { q = JSON.parse(o.body); return { ok: true, json: async () => ({ reply: 'ok' }) }; };
  boot(p2);
  p2.window.document.querySelector('.ai-qbtn').click(); await sleep(50);
  ok(q && q.message === 'How does AI scoring work?', 'quick-reply chips send their question');

  console.log(failures ? `\n${failures} FAILED` : '\nALL WIDGET TESTS PASSED');
  process.exit(failures ? 1 : 0);
})();
