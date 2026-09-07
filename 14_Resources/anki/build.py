#!/usr/bin/env python3
"""Render verified cards into an Anki plain-text import file (tab separated).

Fields: Front, Back, Tags.  No literal newline ever reaches a field -- code is
rendered as <pre> with <br>, so every note is exactly one line of TSV.

The "verified" label under a snippet names the toolchain that ran it, and it is
ASKED FOR at build time rather than typed here: a hand-written version string is
a claim nobody re-checks, and this deck's whole argument is that a card cannot
claim what no program produced.

    python3 verify.py cards_hex && python3 build.py
"""

from __future__ import annotations

import html
import importlib.util
import pathlib
import re
import subprocess

HERE = pathlib.Path(__file__).parent
OUT = HERE  # beside the cards, which is where the README says to import from

PRE = ('<pre style="text-align:left; white-space:pre-wrap; font-size:0.92em; '
       'line-height:1.45; border-left:3px solid #7a7a7a; padding:2px 0 2px 10px; '
       'margin:10px 0; font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;">')

LANG_NAME = {"py": "Python", "rs": "Rust", "sh": "bash", "c": "C"}
COMMENT = {"py": "# ", "rs": "// ", "sh": "# ", "c": "// "}


def toolchain() -> dict[str, str]:
    """Ask each compiler/interpreter what it is. Never hard-code a version."""

    def first(cmd, pattern=None):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True)
        except OSError:
            return "unavailable"
        out = (r.stdout or r.stderr).splitlines()[0].strip()
        if pattern:
            m = re.search(pattern, out)
            if m:
                return m.group(0)
        return out

    return {
        "py": first(["python3", "-V"], r"Python \S+"),
        "rs": first(["rustc", "-V"], r"rustc \S+") + ", edition 2024",
        "c": first(["cc", "--version"]),
        "sh": first(["bash", "--version"], r"bash, version \S+").replace("bash, ", "bash "),
    }


TOOLS = toolchain()


def block(text: str, label: str | None = None) -> str:
    body = html.escape(text).replace("\n", "<br>")
    head = (f'<div style="opacity:.6; font-size:.8em; margin-top:8px;">{label}</div>'
            if label else "")
    return head + PRE + body + "</pre>"


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def render(card):
    lang = card["lang"]
    front = card["front"]
    back_parts = []

    code, on = card.get("code"), card.get("code_on")
    if code and on == "front":
        front += block(code, LANG_NAME[lang])
        if card.get("fails") or card.get("fails_msg"):
            claim = card.get("fails") or card["fails_msg"]
            back_parts.append(block(f"it does not compile -- {claim}", TOOLS[lang] + " says"))
        else:
            back_parts.append(block(card["expect"], "it prints"))

    back_parts.append(card["back"])

    if code and on == "back":
        rendered = code
        if card.get("expect"):
            c = COMMENT[lang]
            rendered += "\n\n" + "\n".join(c + l for l in card["expect"].split("\n"))
        back_parts.append(block(rendered, f"verified &mdash; {TOOLS[lang]}"))

    if card.get("bridge"):
        back_parts.append('<div style="opacity:.85; font-size:.95em; border-top:1px solid #9995; '
                          'margin-top:12px; padding-top:8px;">' + card["bridge"] + "</div>")

    label, url = card["link"]
    back_parts.append(f'<div style="margin-top:10px; font-size:.9em;">&rarr; '
                      f'<a href="{url}">{html.escape(label)}</a></div>')

    back = "<br>".join(back_parts)
    for f in (front, back):
        assert "\t" not in f and "\n" not in f, card["id"]
    return front, back, card["tags"]


def build(name, filename):
    m = load(name)
    lines = ["#separator:tab", "#html:true", "#notetype:Basic",
             f"#deck:{m.DECK}", "#tags column:3"]
    for card in m.CARDS:
        lines.append("\t".join(render(card)))
    path = OUT / filename
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{path.name}: {len(m.CARDS)} cards -> {m.DECK}")
    for lang, ver in sorted(TOOLS.items()):
        print(f"    {lang:<3} {ver}")
    return path


if __name__ == "__main__":
    build("cards_hex", "Encodings_Hex.txt")
