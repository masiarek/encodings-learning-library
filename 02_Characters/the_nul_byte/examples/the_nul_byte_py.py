"""U+0000: an ordinary character that almost nothing will carry.

Run:  python3 the_nul_byte_py.py
"""

import csv
import io
import json
import os
import subprocess
import sqlite3
import unicodedata
import xml.etree.ElementTree as ET


def attempt(label, fn):
    """Call fn and print either what it returned or how it refused."""
    try:
        fn()
        print(f"   {label:<32} -> no error")
    except Exception as exc:
        print(f"   {label:<32} -> {type(exc).__name__}: {exc}")


print("1. U+0000 IS AN ORDINARY CHARACTER, AND ORDINARY UTF-8")
nul = "\x00"
print(f"   ord(nul)                        = {ord(nul)}")
print(f"   category is 'Cc' (a control)    = {unicodedata.category(nul) == 'Cc'}")
print(f"   nul.encode('utf-8')             = {nul.encode('utf-8')!r}   one byte, no escape hatch needed")
print(f"   b'\\x00'.decode('utf-8')         = {b'\x00'.decode('utf-8')!r}   every validator accepts it")
print(f"   nul.encode('utf-16-le')         = {nul.encode('utf-16-le')!r}")
attempt("unicodedata.name(nul)", lambda: unicodedata.name(nul))
print(f"   unicodedata.lookup('NULL')      = {unicodedata.lookup('NULL')!r}   it has no Name, but it has an alias")
print()

print("2. PYTHON HOLDS IT WITHOUT COMPLAINT")
s = "ab\x00cd"
print(f"   s = {s!r}")
print(f"   len(s)                          = {len(s)}   five characters; NUL is the third")
print(f"   s.encode().decode() == s        = {s.encode().decode() == s}")
print(f"   s.split(chr(0))                 = {s.split(chr(0))}")
print(f"   sorted(['b', nul, 'a'])         = {sorted(['b', nul, 'a'])}   it sorts before everything")
print("   Nothing above is special-cased. To Python it is a character like any other.")
print()

print("3. FOUR PLACES PYTHON STOPS YOU, AND ALL FOR THE SAME REASON")
attempt("open('a\\x00b')", lambda: open("a\x00b"))
attempt("os.stat('a\\x00b')", lambda: os.stat("a\x00b"))
attempt("subprocess.run(['echo', s])", lambda: subprocess.run(["echo", s]))
attempt("os.environ['A\\x00B'] = 'x'", lambda: os.environ.__setitem__("A\x00B", "x"))
print("   Each of those hands the string to the operating system, whose interface is")
print("   NUL-terminated C strings. Python refuses rather than let the value be cut.")
print()

print("4. THE CONTAINERS: WHO WILL CARRY A NUL?")
print(f"   json.dumps(s)                   = {json.dumps(s)}   escaped, and legal JSON")
print(f"   json.loads(that) == s           = {json.loads(json.dumps(s)) == s}")
attempt("json.loads('\"a\\x00b\"')", lambda: json.loads('"a\x00b"'))
print("   (a RAW control character inside a JSON string is invalid; the escape is not)")

buf = io.StringIO()
csv.writer(buf).writerow([s, "c"])
row = next(csv.reader(io.StringIO(buf.getvalue())))
print(f"   csv round-trip                  = {row[0] == s}   csv carries it and says nothing")

element = ET.Element("a")
element.text = s
written = ET.tostring(element)
print(f"   ET.tostring(...)                = {written!r}")
attempt("ET.fromstring(that)", lambda: ET.fromstring(written))
attempt("ET.fromstring('<a>&#0;</a>')", lambda: ET.fromstring("<a>&#0;</a>"))
print("   XML 1.0 has no way to spell U+0000 at all -- not as a raw byte and not as a")
print("   character reference -- so Python's writer produced a document that Python's")
print("   own parser refuses. Written, and unreadable.")

db = sqlite3.connect(":memory:")
db.execute("create table t(s text)")
db.execute("insert into t values (?)", (s,))
back, length, hexed = db.execute("select s, length(s), hex(s) from t").fetchone()
print(f"   sqlite: value comes back whole   = {back == s}")
print(f"   sqlite: length(s) says           = {length}   ...for a five-character string")
print(f"   sqlite: hex(s) says              = {hexed}   all five bytes are stored")
print("   The row is intact; SQL's own string function stopped at the NUL. That is")
print("   sizeof against strlen again, one layer up, inside a database.")
print()

print("5. WHY IT IS THE ONE SAFE SEPARATOR")
names = ["holiday\nphotos.txt", "notes.txt"]
print(f"   two filenames, one with a newline in it: {names}")
joined_nl = "\n".join(names)
joined_nul = "\x00".join(names)
print(f"   split on '\\n'  -> {joined_nl.split(chr(10))}   three names, and only two files")
print(f"   split on '\\0'  -> {joined_nul.split(chr(0))}   right, because a name cannot hold a NUL")
print("   A separator has to be a byte the data cannot contain. A Unix filename may")
print("   hold any byte but two -- '/' and NUL -- and '/' is busy separating directories.")
