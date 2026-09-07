#!/usr/bin/env python3
"""What the kernel reads at offset 0, and what it does when that is wrong.

The shell hides this. Type ./x at a prompt and the shell may rescue a file the
kernel refused, so the defect never surfaces. subprocess.run([path]) is a bare
execve with nothing to catch it, which is why the failures are legible here and
not at a prompt.

Note what is printed for a failure: the exception CLASS and the SYMBOLIC errno.
The message text that comes with them is written by the C library and differs
between macOS and Linux, so it is not a property of the file and cannot be an
answer key.

Run:  python3 the_first_two_bytes_py.py
"""

import errno
import os
import subprocess
import tempfile

# Four files. Only the first is well formed; the others differ from it only in
# bytes that nothing on a screen draws.
FILES = {
    "plain.sh": b'#!/bin/sh\necho "I ran"\n',
    "bom.sh":   b'\xef\xbb\xbf#!/bin/sh\necho "I ran"\n',   # BOM in front of the #!
    "crlf.sh":  b'#!/bin/sh\r\necho "I ran"\r\n',            # CR before each LF
    "none.sh":  b'echo "I ran"\n',                           # no #! at all
}

# The four-byte openings a kernel knows, as bytes. Two are Mach-O (macOS) and
# one is ELF (Linux) — which of them your own /bin/sh starts with is a fact
# about your machine, so this program does not look at any file it did not
# write itself.
MAGIC = [
    (b"#!",                 "a script — read the rest of the line as an interpreter"),
    (b"\x7fELF",            "ELF executable (Linux, BSD)"),
    (b"\xcf\xfa\xed\xfe",   "Mach-O 64-bit, little-endian (macOS, one architecture)"),
    (b"\xca\xfe\xba\xbe",   "Mach-O universal binary (macOS, several architectures)"),
]


def classify(head: bytes) -> str:
    """What a kernel decides, from the first bytes and nothing else."""
    for sig, what in MAGIC:
        if head.startswith(sig):
            return what
    return "no signature — ENOEXEC, the kernel will not run this"


def hexed(bs: bytes) -> str:
    return " ".join(f"{b:02x}" for b in bs)


tmp = tempfile.mkdtemp()
paths = {}
for name, body in FILES.items():
    p = os.path.join(tmp, name)
    with open(p, "wb") as f:
        f.write(body)
    os.chmod(p, 0o755)
    paths[name] = p

print("1. THE FIRST FOUR BYTES OF EACH FILE")
for name in FILES:
    head = FILES[name][:4]
    print(f"   {name:9} {hexed(head):12} {classify(head)}")
print("   All four are executable, all four end in .sh, and file(1) calls three")
print("   of them shell scripts. None of that reaches the kernel.")

print()
print("2. THE #! IS TWO ASCII BYTES, AND ITS OFFSET IS THE WHOLE RULE")
print(f"   ord('#') = {ord('#')} = 0x{ord('#'):02x}     ord('!') = {ord('!')} = 0x{ord('!'):02x}")
print(f"   plain.sh  finds #! at offset {FILES['plain.sh'].index(b'#!')}")
print(f"   bom.sh    finds #! at offset {FILES['bom.sh'].index(b'#!')}")
print("   Offset 3 is not offset 0. The kernel does not search; it compares.")

print()
print("3. execve(), WITH NO SHELL TO CATCH THE REFUSAL")
for name, p in paths.items():
    try:
        r = subprocess.run([p], capture_output=True, text=True)
        print(f"   {name:9} ran      rc={r.returncode}  stdout={r.stdout.strip()!r}")
    except OSError as e:
        code = errno.errorcode.get(e.errno, str(e.errno))
        print(f"   {name:9} refused  {type(e).__name__}  errno {e.errno} ({code})")
print("   Three different outcomes for four files that look identical on screen.")

print()
print("4. WHY THE TWO REFUSALS ARE NOT THE SAME REFUSAL")
for name in ("bom.sh", "crlf.sh"):
    body = FILES[name]
    if body.startswith(b"#!"):
        interp = body[2:body.index(b"\n")].decode("ascii")
        print(f"   {name:9} kernel sees #!, interpreter = {interp!r}")
    else:
        print(f"   {name:9} kernel sees {hexed(body[:2])}, not 23 21 — no interpreter is read")
print("   bom.sh   ENOEXEC: 'this is not a program'. The #! was never found.")
print("   crlf.sh  ENOENT:  'that interpreter does not exist'. The #! WAS found,")
print("            and the path read out of it has a 13 on the end.")
print("   The second is the one that reads as a lie: the file it names is there.")

print()
print("5. WHY strip() DOES NOT SAVE bom.sh")
raw = FILES["bom.sh"][:5]
print(f"   raw first bytes        {hexed(raw)}")
print(f"   .strip() changes it?   {raw.strip() != raw}")
print(f"   chr(0xFEFF).isspace()  {chr(0xFEFF).isspace()}")
print("   U+FEFF is named ZERO WIDTH NO-BREAK SPACE and is not in Unicode's")
print("   White_Space property, so no strip anywhere will remove it. It is")
print("   content, and at offset 0 of an executable it is fatal content.")

print()
print("6. THE CHECK WORTH PUTTING IN CI")
for name, body in FILES.items():
    ok = body.startswith(b"#!") and b"\r" not in body.split(b"\n")[0]
    print(f"   {name:9} first line is a usable shebang: {ok}")
print("   Two questions, both about bytes: does it START with 23 21, and is the")
print("   first line free of 0d. Neither is answerable from the rendered text.")

for p in paths.values():
    os.unlink(p)
os.rmdir(tmp)
