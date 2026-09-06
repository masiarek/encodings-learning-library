#!/usr/bin/env python3
"""The four rules behind `rg -z` and `rg --pre`, applied by hand in the stdlib.

`rg` is not on either CI runner, so no answer key on this page comes from the
tool. What CAN be checked is the shape: a transform stage that runs first, an
unchanged decode stage after it, a detector that reads the name rather than the
bytes, and a fallback that answers without complaining. All four are a dozen
lines of `gzip`, `zlib` and `pathlib`.

The honest limit is this chapter's usual one: this tests the model, not the tool.
That is why the session on the page is dated and names its machines.
"""

import gzip
import pathlib
import zlib

TEXT = "café utf8\n"
RAW_UTF8 = TEXT.encode("utf-8")
RAW_UTF16 = b"\xff\xfe" + "café utf16\n".encode("utf-16-le")
RAW_UTF32 = b"\xff\xfe\x00\x00" + "café utf32\n".encode("utf-32-le")

# The three marks rg's -E auto tests for, longest first. UTF-32 is deliberately
# absent -- see the ripgrep page; this file inherits that gap on purpose.
RG_BOMS = [(b"\xef\xbb\xbf", "utf-8-sig"), (b"\xff\xfe", "utf-16-le"), (b"\xfe\xff", "utf-16-be")]


def show(label: str, value: object) -> None:
    print(f"   {label:<42} {value}")


def decode_like_rg(raw: bytes) -> str:
    """Stage 2. Exactly the ripgrep page's sniffer, given whatever stage 1 left."""
    for mark, codec in RG_BOMS:
        if raw.startswith(mark):
            return raw.decode(codec) if codec == "utf-8-sig" else raw[2:].decode(codec)
    return raw.decode("utf-8", "replace")


print("RULE 1. TWO STAGES, AND THE SECOND ONE DOES NOT KNOW ABOUT THE FIRST")
for name, raw in [("utf-8", RAW_UTF8), ("utf-16+BOM", RAW_UTF16), ("utf-32+BOM", RAW_UTF32)]:
    packed = gzip.compress(raw, mtime=0)
    show(f"{name}: gzipped to", f"{len(packed)} bytes")
    show(f"{name}: 'café' found after decoding", "café" in decode_like_rg(gzip.decompress(packed)))
print("   True, True, False -- and the False is not about compression. Decompress")
print("   first, then hand the result to the same sniffer, and a UTF-32 file fails")
print("   exactly the way it fails uncompressed: the mark ff fe 00 00 begins with")
print("   UTF-16LE's ff fe, so it is read as UTF-16 and every letter gets a NUL.")
print("   That is the point of the ordering. -z and --pre are a stage BEFORE the")
print("   encoding stage; they add a step and change nothing about the step after.")

print()
print("RULE 2. THE DETECTOR READS THE NAME; THE MAGIC IS IN THE BYTES")
packed = gzip.compress(RAW_UTF8, mtime=0)
for name in ("plain.txt.gz", "notgz.txt"):
    by_name = pathlib.PurePath(name).suffix == ".gz"
    by_magic = packed[:2] == b"\x1f\x8b"
    show(f"{name}: suffix says gzip?", by_name)
    show(f"{name}: first two bytes say gzip?", by_magic)
print("   Identical bytes, two names, two answers. rg -z asks the first question")
print("   and `file` asks the second, which is why `file` can call notgz.txt")
print("   application/gzip on the very run where rg searches it as text. Neither")
print("   is buggy; only one of them opened the file to find out.")

print()
print("RULE 3. AN OFFSET IS INTO THE LAST STREAM, NOT THE FILE")
show("'utf16' at byte N of the FILE", RAW_UTF16.find("utf16".encode("utf-16-le")))
show("'utf16' at byte N after decoding", decode_like_rg(RAW_UTF16).encode("utf-8").find(b"utf16"))
show("file is this many bytes", len(RAW_UTF16))
show("decoded text is this many bytes", len(decode_like_rg(RAW_UTF16).encode("utf-8")))
print("   Twelve and six. rg -b reports the second, because that is the stream it")
print("   printed from -- and the same applies after -z or --pre, where the file")
print("   on disk may share no bytes at all with what was searched. So a -b offset")
print("   is a position in rg's output, not a `dd skip=` argument, unless nothing")
print("   transformed the input.")

print()
print("RULE 4. THE FALLBACK ANSWERS. IT DOES NOT COMPLAIN")
stored = zlib.compress(RAW_UTF8, 0)      # level 0: deflate STORES the bytes as-is
deflated = zlib.compress(RAW_UTF8 * 20, 9)
show("searching the COMPRESSED bytes, level 0", RAW_UTF8.strip() in stored)
show("searching the COMPRESSED bytes, level 9", RAW_UTF8.strip() in deflated)
print("   True then False, from the same query against the same content. When the")
print("   decompressor is missing, rg silently falls back to reading the file")
print("   uncompressed -- and what you get back depends on how well the file")
print("   happened to compress. A small or already-compact payload is stored")
print("   almost verbatim, so the search 'works'; a real one does not, and reports")
print("   no match. Two different wrong answers, one missing binary, and neither")
print("   run says a word about it unless you pass --debug.")
