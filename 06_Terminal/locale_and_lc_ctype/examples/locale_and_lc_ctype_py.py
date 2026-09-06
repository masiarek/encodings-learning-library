"""Python does not obey the locale, and has not since 3.7.

The shell half of this lesson shows tool after tool changing with LC_CTYPE.
Python is the one that reads the same C locale and declines — which is a mercy,
and is why a bug that bites `wc` inside a container does not bite the Python
program sitting next to it. Worth knowing exactly what it declines to do.

Every measurement below is taken in a CHILD interpreter whose environment this
file sets on the line above it, so the answers do not depend on how you started
this one. That is the discipline a lesson about the environment has to keep.

Run:  python3 locale_and_lc_ctype_py.py
"""

import os
import subprocess
import sys

C_LOCALE = {"LC_ALL": "C", "LANG": "C"}


def child(code, /, **env):
    """Run `code` in a fresh interpreter under a C locale, plus `env`."""
    e = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    e.update(C_LOCALE)
    e.update(env)
    # No -I here: isolated mode implies -E, and -E would ignore the very
    # variables this lesson is about.
    return subprocess.run([sys.executable, "-c", code], env=e,
                          capture_output=True, text=True).stdout.rstrip()


print("1. A C LOCALE, AND NOTHING ELSE SET")
print("     LC_ALL=C  LANG=C  PYTHONUTF8 unset  -- the default in a container,")
print("     a cron job, a systemd unit and most CI runners.")
print()

print("2. WHAT THE LOCALE SAYS, AND WHAT PYTHON DOES ANYWAY")
print(child(r"""
import locale, sys
# The locale's own encoding is named differently per platform -- 'US-ASCII' on
# macOS, 'ANSI_X3.4-1968' on glibc -- so ask whether it IS utf-8, never what it
# is called. getpreferredencoding() is a different question: what Python will
# actually use. The gap between the two lines is the whole section.
u = lambda s: s.lower().replace('_', '-') == 'utf-8'
print(f"     locale.getencoding() is utf-8             {u(locale.getencoding())}")
print(f"     locale.getpreferredencoding() is utf-8    {u(locale.getpreferredencoding(False))}")
print(f"     sys.flags.utf8_mode                       {sys.flags.utf8_mode}")
print(f"     sys.stdout.encoding is utf-8              {u(sys.stdout.encoding)}")
print(f"     sys.getfilesystemencoding() is utf-8      {u(sys.getfilesystemencoding())}")
"""))
print("     UTF-8 Mode turned ITSELF on, because the locale is C (PEP 540).")
print("     Nothing in the environment asked for it. Python read the same")
print("     setting `wc` read and decided a machine claiming to be ASCII-only")
print("     is describing its own configuration, not its data.")
print()

print("3. WHAT THAT IS PROTECTING YOU FROM")
with open("_locale_demo.txt", "w", encoding="utf-8") as fh:
    fh.write("café\n")
read_it = (
    "import sys\n"
    "print('utf8_mode', sys.flags.utf8_mode, end='   ')\n"
    "try:\n"
    "    open('_locale_demo.txt').read(); print('open() read it: OK')\n"
    "except UnicodeDecodeError as exc:\n"
    "    print('open() read it:', type(exc).__name__)\n")
for mode in ("1", "0"):
    print(f"     PYTHONUTF8={mode}   {child(read_it, PYTHONUTF8=mode)}")
os.remove("_locale_demo.txt")
print("     Same file, same locale, one variable apart. With the mode off,")
print("     open() takes its default encoding from the C locale -- ASCII --")
print("     and the second byte of the e-acute ends the program. That is the")
print("     crash 3.7 stopped shipping, and it is still one variable away.")
print()

print("4. THE ONLY SPELLING THAT IS NOT A GUESS")
print("     open(path, encoding='utf-8')    says what it means, everywhere")
print("     open(path)                      asks the locale, unless UTF-8 Mode")
print("     open(path, encoding=None)       the same guess, spelled worse")
print("     Pass encoding= and nothing on this page can reach your program.")
