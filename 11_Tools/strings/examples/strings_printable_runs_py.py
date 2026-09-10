"""strings(1) is one regular expression; what differs between builds is the table.

strings prints every run of four or more bytes that its table calls printable.
That is re.findall over bytes, so the only thing two builds can disagree about
is the table. This program writes down the four tables measured on 2026-09-10
(GNU binutils 2.42 and 2.44; Apple's strings from the macOS 26.6.2 command-line tools,
which uses a different table depending on how the file reaches it) and runs the
same inputs through each. It calls no tool: every line below is arithmetic over
those four sets, so it prints the same on every machine.

Run:  python3 strings_printable_runs_py.py
"""
import re


def span(lo, hi):
    return set(range(lo, hi + 1))


ASCII = span(0x20, 0x7E)                                   # space to tilde: 95 bytes
TABLES = {
    "GNU strings":          ASCII | {0x09},                # + tab
    "Apple, file argument": ASCII | {0x0C},                # + form feed
    "Apple, stdin, C":      ASCII,
    "Apple, stdin, UTF-8":  ASCII | span(0xA0, 0xFF) - {0xAD},
}


def runs(data, table, n=4):
    """strings(1): every maximal run of bytes in `table` that is n or longer."""
    found, run = [], bytearray()
    for b in data + b"\x00":                               # a sentinel ends the last run
        if b in table:
            run.append(b)
            continue
        if len(run) >= n:
            found.append(bytes(run))
        run.clear()
    return found


def hexranges(table):
    vals = sorted(table)
    out, start, prev = [], vals[0], vals[0]
    for v in vals[1:] + [None]:
        if v is not None and v == prev + 1:
            prev = v
            continue
        out.append(f"{start:02x}" if start == prev else f"{start:02x}-{prev:02x}")
        if v is not None:
            start = prev = v
    return " ".join(out)


ZOO = b"hello\x00\x01\x02world\n"

print("1. THE WHOLE TOOL IS ONE REGULAR EXPRESSION")
print(f"   zoo = {ZOO!r}")
print(r"   re.findall(rb'[\x20-\x7e]{4,}', zoo)  ->", re.findall(rb"[\x20-\x7e]{4,}", ZOO))
print("   Runs of four or more bytes from space to tilde; every other byte ends")
print("   a run and is thrown away. That is strings. The rest of this program is")
print("   about the one thing builds disagree on: which bytes count as printable.")

print()
print("2. FOUR TABLES, ONE PER BUILD AND INPUT PATH")
for name, table in TABLES.items():
    print(f"   {name:<21} {len(table):>3} bytes   {hexranges(table)}")
print("   Three are ASCII plus at most one control character. The fourth is what")
print("   Apple's strings uses when the file arrives on STDIN in a UTF-8 locale:")
print("   it also keeps every byte from a0 to ff except ad (the soft hyphen),")
print("   each judged as if it were a Latin-1 character on its own.")

INPUTS = [
    ("tab",           b"abcd\tefgh\n"),
    ("café, UTF-8",   "café bar\n".encode("utf-8")),
    ("café, Latin-1", "café bar\n".encode("latin-1")),
    ("żółw, UTF-8",   "żółw\n".encode("utf-8")),
    ("…, UTF-8",      "Wait… what\n".encode("utf-8")),
]

print()
print("3. FIVE INPUTS THROUGH FOUR TABLES")
for label, data in INPUTS:
    print(f"   {label} = {data!r}")
    for name, table in TABLES.items():
        print(f"      {name:<21} {runs(data, table)}")
print("   On these five inputs the first three tables differ only over the tab.")
print("   The fourth keeps café whole, cuts żółw after five bytes, and splits the")
print("   ellipsis in two.")

print()
print("4. A RUN OF PRINTABLE BYTES IS NOT NECESSARILY TEXT")
print("   Every UTF-8 input above, through the fourth table, then decoded:")
for label, data in INPUTS[1:]:
    if not label.endswith("UTF-8"):
        continue
    for r in runs(data, TABLES["Apple, stdin, UTF-8"]):
        try:
            r.decode("utf-8")
            verdict = "valid UTF-8"
        except UnicodeDecodeError as e:
            verdict = f"NOT valid UTF-8 ({type(e).__name__})"
        print(f"   {label:<12} {r!r:<24} {verdict}")
print("   All three inputs were valid UTF-8. Two came out broken: the ł cut after")
print("   its first byte, and the ellipsis spread over two runs with its middle")
print("   byte gone. The one that came out whole was kept for the wrong reason —")
print("   c3 and a9 are Ã and © in Latin-1, and this table is Latin-1's.")
print("   A tool that never decodes cannot fail to decode; it can still hand you")
print("   bytes that no longer do.")

print()
print("5. WHAT A STRINGS FOR UTF-8 WOULD HAVE TO DO")
NOT_TEXT = r"[\x00-\x1f\x7f-\x9f\udc80-\udcff]"           # controls, and bytes that did not decode


def text_runs(data, n=4):
    """Decode first, then find runs of n or more characters that are not NOT_TEXT."""
    text = data.decode("utf-8", errors="surrogateescape")
    return re.findall(f"[^{NOT_TEXT[1:-1]}]{{{n},}}", text)


for label, data in INPUTS:
    found = " | ".join(f"'{r}'" for r in text_runs(data))
    print(f"   {label:<14} {found}")
print("   Decode, then count characters instead of bytes: a character counts")
print("   unless it is a control character or a byte that did not decode (which")
print("   surrogateescape keeps as a marker, so it still ends a run). Now żółw is")
print("   four characters and a run, the ellipsis stays in one piece, and the")
print("   Latin-1 file gets exactly the answer strings gave it. That decode step")
print("   is the part strings leaves to you.")
