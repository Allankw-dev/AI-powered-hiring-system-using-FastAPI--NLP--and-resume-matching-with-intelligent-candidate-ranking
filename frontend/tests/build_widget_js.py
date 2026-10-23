"""Writes the chat widget's JavaScript (as the browser receives it) to
widget.generated.js so the jsdom test can run it. Streamlit is stubbed, so
Streamlit does not need to be installed."""
import pathlib
import sys
import types

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

st, comp, v1 = (types.ModuleType(n) for n in ("streamlit", "streamlit.components", "streamlit.components.v1"))
v1.html = lambda *a, **k: None
comp.v1, st.components = v1, comp
sys.modules.update({"streamlit": st, "streamlit.components": comp, "streamlit.components.v1": v1})

import chat_widget  # noqa: E402

html = chat_widget.build_html("https://api.example.com/")
js = html[len("<script>"):-len("</script>")]
assert "</" not in js, "payload could close the <script> tag"
(HERE / "widget.generated.js").write_text(js, encoding="utf-8")
print(f"widget.generated.js written ({len(js)} bytes)")
