"""Run from the frontend/tests folder:  python test_chat_widget.py"""
import json
import pathlib
import sys
import types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
st, comp, v1 = (types.ModuleType(n) for n in ("streamlit", "streamlit.components", "streamlit.components.v1"))
v1.html = lambda *a, **k: None
comp.v1, st.components = v1, comp
sys.modules.update({"streamlit": st, "streamlit.components": comp, "streamlit.components.v1": v1})

import chat_widget  # noqa: E402


def test_placeholders_replaced_and_url_escaped():
    html = chat_widget.build_html('https://x.test/"; alert(1); "')
    assert "__API__" not in html and "__CSS__" not in html and "__MARKUP__" not in html
    assert json.dumps('https://x.test/"; alert(1); "') in html  # injected as a safe JS string


def test_payload_cannot_close_script_tag():
    body = chat_widget.build_html("https://x.test")[len("<script>"):-len("</script>")]
    assert "</" not in body


def test_no_inline_handlers_left_in_markup():
    for needle in ("onclick", "onkeydown", "oninput"):
        assert needle not in chat_widget._MARKUP


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
