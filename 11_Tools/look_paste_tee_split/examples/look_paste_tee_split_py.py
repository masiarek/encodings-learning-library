#!/usr/bin/env python3
"""The same four jobs in Python, where the thing the shell tools get wrong is
either impossible to write or has a name in the standard library.

split's problem — a chunk boundary that lands inside a character — is real here
too, and Python ships the fix: an incremental decoder, which is exactly the
buffer `split -b` has nowhere to keep. paste's problem cannot happen, because a
delimiter is a string rather than a list of bytes. look's problem happens
verbatim, under the name `bisect`, and for the same reason.
"""

import bisect
import codecs
import tempfile
from itertools import zip_longest
from pathlib import Path

TEXT = "café naïve"          # 10 characters, 12 bytes
RAW = TEXT.encode("utf-8")


def show(label: str, value: object) -> None:
    print(f"   {label:<44} {value}")


print("1. A CHUNK BOUNDARY IS A BYTE OFFSET, AND CHARACTERS DO NOT CARE")
chunks = [RAW[i:i + 4] for i in range(0, len(RAW), 4)]
show("the bytes", RAW.hex())
show("four-byte chunks", [c.hex() for c in chunks])
failed = []
for n, chunk in enumerate(chunks, 1):
    try:
        chunk.decode("utf-8")
    except UnicodeDecodeError:
        failed.append(n)
show("chunks that will not decode alone", failed)
print("   That is `split -b 4` with a different spelling, and the same result:")
print("   the pieces are not text, only their concatenation is.")

print()
print("2. THE FIX HAS A NAME: AN INCREMENTAL DECODER")
dec = codecs.getincrementaldecoder("utf-8")()
out = [dec.decode(c) for c in chunks]
show("what each chunk yielded", out)
show("joined", "".join(out))
show("...equals the original", "".join(out) == TEXT)
show("dec.decode(b'', final=True) at the end", repr(dec.decode(b"", final=True)))
print("   Chunk 1 handed back three characters and kept a dangling c3; chunk 2")
print("   completed it and returned the é first. The decoder is holding the")
print("   partial character between calls — that is the state a stream decoder")
print("   has and a file-splitter does not, which is the whole difference.")
print("   Call it with final=True at the end: a leftover half-character there")
print("   is a truncated file, and only that call will tell you.")

print()
print("3. A DELIMITER IS A STRING, NOT A LIST OF BYTES")
cols = [["a1", "a2"], ["b1", "b2"], ["c1", "c2"]]
rows = ["é".join(r) for r in zip(*cols)]
show("'é'.join(row)", rows)
show("the bytes of row 1", rows[0].encode("utf-8").hex())
print("   One é between each pair, c3 a9 both times. The shell's paste -d takes")
print("   a LIST of delimiters and reads it a byte at a time, so the same")
print("   request there puts c3 after the first column and a9 after the second.")
print("   Python cannot make that mistake: you named a string, not a set.")
short = [["a1", "a2"], ["b1"]]
show("zip_longest, fillvalue=''", ["\t".join(r) for r in zip_longest(*short, fillvalue="")])
print("   And that is paste's other rule — a short column becomes empty fields,")
print("   not a short row — written down where you can see it.")

print()
print("4. bisect IS look, AND IT FAILS THE SAME WAY")
words = ["Ada", "bob", "Cara", "dan"]           # sorted case-insensitively
show("the list", words)
show("'Cara' in words", "Cara" in words)
i = bisect.bisect_left(words, "Cara")
show("bisect_left(words, 'Cara')", i)
show("...the element actually there", words[i] if i < len(words) else "(past the end)")
show("found by binary search?", i < len(words) and words[i] == "Cara")
print("   The word is in the list and the binary search cannot find it, because")
print("   the list is ordered case-insensitively and the comparison is by code")
print("   point, where every capital sorts before every lowercase letter. Two")
print("   orders, one search, no error. `look` on a file sorted by anything but")
print("   the order it compares with is this bug with a file behind it — and a")
print("   locale is the commonest way to end up with two orders.")

print()
print("5. THE tee GUARANTEE IS SPELLED 'b'")
DOS = "caf\u00e9\r\nsecond\r\n"
with tempfile.TemporaryDirectory() as d:
    f = Path(d) / "dos.txt"
    f.write_bytes(DOS.encode("utf-8"))
    show("the bytes on disk", f.read_bytes().hex())
    show("read_bytes() gives them back", f.read_bytes() == DOS.encode("utf-8"))
    show("read_text() gives back", repr(f.read_text(encoding="utf-8")))
    show("...same bytes?", f.read_text(encoding="utf-8").encode("utf-8") == DOS.encode("utf-8"))
print("   Two doors onto one file, and only one of them is tee. The text door")
print("   decoded and then translated the line endings, so what your code got")
print("   is not what the file holds — and it will not tell you, because for")
print("   almost every program that translation is the helpful thing to do.")
print("   When the question is what a pipeline did to the bytes, ask in binary:")
print("   that is the mode with no text model, which is what tee is.")
