#!/usr/bin/env python3
"""The same program, run twice: once with a real terminal on stdout, once with
a pipe. Then the two answers side by side.

Why it is written this way. Every example in this library runs with its output
captured, so a program that asks `sys.stdout.isatty()` can only ever see the
piped branch — it would describe a fork in the road it cannot stand at. The
`pty` module fixes that: it opens a real pseudo-terminal, and `subprocess` runs
the same child down both roads.

The environment is built here, in view, rather than inherited. `tools/run_examples.py`
pins `PYTHONUTF8=1`, which is one of the very settings this page is about, and
a child that inherited it could not show section 4 at all.

Run:  python3 pipe_is_not_a_terminal_py.py
"""

import os
import pty
import subprocess
import sys

# ---------------------------------------------------------------- the child

if len(sys.argv) > 1 and sys.argv[1] == "--report":
    o, e = sys.stdout, sys.stderr
    print(f"stdout isatty={str(o.isatty()):<5} encoding={o.encoding:<7} "
          f"errors={o.errors:<16} line_buffering={o.line_buffering}")
    print(f"stderr isatty={str(e.isatty()):<5} encoding={e.encoding:<7} "
          f"errors={e.errors:<16} line_buffering={e.line_buffering}")
    try:
        o.write("euro=€\n")
        o.flush()
    except UnicodeEncodeError as exc:
        print(f"euro   -> {type(exc).__name__} (reason: {exc.reason})")
    sys.exit(0)

if len(sys.argv) > 1 and sys.argv[1] == "--interleave":
    for i in (1, 2):
        sys.stdout.write(f"OUT {i}\n")
        sys.stderr.write(f"ERR {i}\n")
    sys.exit(0)

if len(sys.argv) > 1 and sys.argv[1] == "--hard-exit":
    sys.stdout.write("the child wrote this line\n")
    os._exit(0)                      # no flush, no atexit, nothing

# --------------------------------------------------------------- the parent

ME = os.path.abspath(__file__)
BASE = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}


def child_env(**extra: str) -> dict[str, str]:
    """A whole environment, spelled out. Nothing is inherited except PATH."""
    return {**BASE, **extra}


def down_a_pipe(arg: str, env: dict[str, str], merge_stderr: bool = False) -> str:
    err = subprocess.STDOUT if merge_stderr else subprocess.DEVNULL
    p = subprocess.run([sys.executable, ME, arg], stdout=subprocess.PIPE,
                       stderr=err, env=env)
    return p.stdout.decode("utf-8", "backslashreplace")


def down_a_terminal(arg: str, env: dict[str, str], merge_stderr: bool = False) -> str:
    """The same run, with a real pty on stdout instead of a pipe."""
    controller, follower = pty.openpty()
    proc = subprocess.Popen([sys.executable, ME, arg], stdout=follower,
                            stderr=follower if merge_stderr else subprocess.DEVNULL,
                            env=env)
    os.close(follower)               # so the read below sees end-of-file
    chunks = []
    while True:
        try:
            data = os.read(controller, 4096)
        except OSError:              # Linux raises EIO here; macOS returns b""
            break
        if not data:
            break
        chunks.append(data)
    proc.wait()
    os.close(controller)
    # A terminal turns every \n into \r\n on the way out. That is the tty
    # discipline, not the program, so it is undone before comparing.
    return b"".join(chunks).decode("utf-8", "backslashreplace").replace("\r\n", "\n")


def pair(label: str, arg: str, env: dict[str, str]) -> None:
    print(f"   {label}")
    for road, text in (("terminal", down_a_terminal(arg, env)),
                       ("pipe    ", down_a_pipe(arg, env))):
        for line in text.strip().splitlines():
            print(f"     {road}  {line}")


C = child_env(LC_ALL="C", LANG="C")

print("1. THE SAME PROGRAM, TWO STDOUTS")
pair("LC_ALL=C, nothing else set", "--report", C)
print("   Four properties on stdout, and exactly one of them moved. isatty()")
print("   answered the question honestly both times; line_buffering followed")
print("   it; encoding and errors did not budge.")
print("   The stderr rows are the control. Its line_buffering is True on both")
print("   roads — stderr is line-buffered whether or not anyone is watching,")
print("   which is the whole reason a diagnostic reaches you and the stdout")
print("   line above it does not. (Its isatty answer is about the DEVNULL and")
print("   pipe this parent handed it, and is not the point.)")

print()
print("2. THE ENCODING FORK IS REAL — AND THE TTY IS NOT WHAT DECIDES IT")
pair("PYTHONUTF8=0 (and LC_ALL=C)", "--report", child_env(LC_ALL="C", PYTHONUTF8="0"))
pair("PYTHONIOENCODING=ascii", "--report", child_env(LC_ALL="C", PYTHONIOENCODING="ascii"))
print("   There is the UnicodeEncodeError — and it happened on BOTH roads, not")
print("   on the piped one. On this platform sys.stdout's encoding comes from")
print("   PYTHONIOENCODING, then UTF-8 Mode, then the locale, and isatty() is")
print("   not consulted at any step. Piping a program into `cat` does not")
print("   change what it can print; changing the locale does.")
print("   (Windows is the other story, and this library cannot measure it: a")
print("   console there gets a UTF-8 writer and a redirected stream gets the")
print("   ANSI code page, so on Windows the tty really is the fork. That is")
print("   where the folklore comes from.)")

print()
print("3. WHAT LINE BUFFERING ACTUALLY COSTS")
print("   The child alternates stdout and stderr: OUT 1, ERR 1, OUT 2, ERR 2.")
print("   Both streams are pointed at the same place, so the order you read is")
print("   the order the bytes arrived.")
print("     down a terminal:  " + " ".join(down_a_terminal("--interleave", C, True).split()))
print("     down a pipe:      " + " ".join(down_a_pipe("--interleave", C, True).split()))
print("   Through the pipe the two ERR lines came out FIRST, although the")
print("   program wrote OUT 1 before either of them. stderr is never buffered")
print("   and stdout now is, so the whole of stdout was still sitting in its")
print("   own buffer when the program ended, and went out in one piece at")
print("   exit. Down the terminal the order is the order it was written in.")
print("   How big that buffer is deliberately does not appear here: it is")
print("   8192 bytes up to Python 3.13 and 131072 in 3.14, so the size is a")
print("   fact about the interpreter and not about the program. The page has")
print("   the numbers in a dated table.")
print("   Every interleaved log you have ever read out of order is this.")

print()
print("4. AND WHERE THE BUFFER GOES WHEN THE PROCESS DOES NOT")
U = child_env(LC_ALL="C", PYTHONUNBUFFERED="1")
print(f"     down a terminal, default        {down_a_terminal('--hard-exit', C).strip()!r}")
print(f"     down a pipe,     default        {down_a_pipe('--hard-exit', C).strip()!r}")
print(f"     down a pipe,     PYTHONUNBUFFERED=1  {down_a_pipe('--hard-exit', U).strip()!r}")
print("   The child wrote a line and then called os._exit, which does not flush.")
print("   Down the terminal the line had already left at the newline. Down a")
print("   pipe it is simply gone — no error, no exit status, no trace of it")
print("   anywhere. Same program, same byte, one of them on the floor.")
print("   This is why a crashed job's last words are missing from the log and")
print("   present on the screen, and why PYTHONUNBUFFERED is in every")
print("   Dockerfile anyone has ever debugged at 2am.")
