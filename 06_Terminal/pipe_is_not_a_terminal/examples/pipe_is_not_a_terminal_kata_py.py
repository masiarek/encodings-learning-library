#!/usr/bin/env python3
"""Kata solution: the same script run twice, and the three questions.

Same shape as the lesson's example — a pty for one road, a pipe for the other,
and an environment built here rather than inherited, because the runner pins
PYTHONUTF8 and that is one of the settings under test.

Run:  python3 pipe_is_not_a_terminal_kata_py.py
"""

import os
import pty
import subprocess
import sys

if len(sys.argv) > 1 and sys.argv[1] in ("--show", "--show-hard"):
    o = sys.stdout
    print(f"isatty={o.isatty()}  encoding={o.encoding}  line_buffering={o.line_buffering}")
    try:
        print("euro=€")
    except UnicodeEncodeError as exc:
        print(f"euro raised {type(exc).__name__}")
    if sys.argv[1] == "--show-hard":
        os._exit(0)                   # the third question: no flush on the way out
    sys.exit(0)

ME = os.path.abspath(__file__)


def run(env: dict[str, str], terminal: bool, arg: str = "--show") -> str:
    if not terminal:
        p = subprocess.run([sys.executable, ME, arg], stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, env=env)
        return p.stdout.decode("utf-8", "backslashreplace")
    controller, follower = pty.openpty()
    proc = subprocess.Popen([sys.executable, ME, arg], stdout=follower,
                            stderr=subprocess.DEVNULL, env=env)
    os.close(follower)
    out = b""
    while True:
        try:
            data = os.read(controller, 4096)
        except OSError:
            break
        if not data:
            break
        out += data
    proc.wait()
    os.close(controller)
    return out.decode("utf-8", "backslashreplace").replace("\r\n", "\n")


PATH = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
PLAIN = {**PATH, "LC_ALL": "C"}
NO_UTF8 = {**PATH, "LC_ALL": "C", "PYTHONUTF8": "0"}


def show(title: str, env: dict[str, str], arg: str = "--show") -> None:
    print(f"   {title}")
    for road, terminal in (("python3 show.py       ", True),
                           ("python3 show.py | cat ", False)):
        body = run(env, terminal, arg).strip() or "(nothing arrived at all)"
        for line in body.splitlines():
            print(f"     {road} {line}")


print("1. WHICH LINES DIFFER")
show("LC_ALL=C, the ordinary case", PLAIN)
print("   One property out of three. isatty() reports what it was asked and")
print("   line_buffering follows it; encoding is identical on both roads. The")
print("   euro printed fine down the pipe, which answers the second question")
print("   before it is asked.")

print()
print("2. THE UnicodeEncodeError, AND WHAT REALLY CAUSES IT")
show("PYTHONUTF8=0 (still LC_ALL=C)", NO_UTF8)
print("   Both roads raised it, and both roads say so in the same words. The")
print("   C locale means ASCII, UTF-8 Mode was switched off, and stdout could")
print("   not encode a euro sign no matter who was on the other end. The")
print("   locale causes this, not the pipe.")
print("   Anyone who has seen it appear on adding '| cat' was on Windows,")
print("   where a console really does get a different writer from a redirected")
print("   stream — the one platform this library cannot measure.")

print()
print("3. WHICH RUN LOSES ITS OUTPUT")
print("   The same script again, with one line added at the end: os._exit(0),")
print("   which skips every flush on the way out.")
show("LC_ALL=C, ending in os._exit(0)", PLAIN, "--show-hard")
print("   The pipe run lost BOTH lines — not truncated, not garbled, gone,")
print("   with exit status 0 and nothing on stderr. Down the terminal the same")
print("   two lines had already left at their newlines. That is the price of")
print("   the one property that changed in section 1, and it is charged only")
print("   when something goes wrong, which is when you needed the output.")
print("   The fixes, in order of how much you should like them:")
print("     flush=True on the print that matters      precise")
print("     sys.stdout.reconfigure(line_buffering=True)  for a whole stream")
print("     python3 -u  /  PYTHONUNBUFFERED=1         blunt, and fine in a")
print("                                               container")
print("     never call os._exit                       the actual bug here")
