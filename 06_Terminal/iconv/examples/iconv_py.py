#!/usr/bin/env python3
"""iconv, written out in Python — and the two places the two disagree.

`iconv -f X -t Y` is `data.decode(X).encode(Y)`, with the same three parts and
the same failure. What Python adds is a *name* for each error policy and a
refusal where iconv waves the bytes through.

Run:  python3 iconv_py.py
"""

LATIN1 = b"caf\xe9 \xa4 100\n"          # café ¤ 100, one byte per character
UTF8 = LATIN1.decode("iso-8859-1").encode("utf-8")


def hx(b: bytes) -> str:
    return b.hex(" ")


print("1. THE SAME THREE PARTS")
print(f"   the file (ISO-8859-1)    {hx(LATIN1)}")
print(f"   .decode('iso-8859-1')    {LATIN1.decode('iso-8859-1')!r}")
print(f"   .encode('utf-8')         {hx(UTF8)}")
print("   iconv -f X -t Y is one expression: decode with the table you claim")
print("   the bytes are in, encode with the table you want. The str in the")
print("   middle is what iconv never gives you a name for.")

print()
print("2. THE SAME SILENT WRONG ANSWER")
wrong = UTF8.decode("iso-8859-1")
print(f"   UTF-8 bytes .decode('iso-8859-1') -> {wrong!r}")
print(f"   .encode('utf-8')                  -> {hx(wrong.encode('utf-8'))}")
print("   No exception, because Latin-1 has all 256 bytes. Python is exactly as")
print("   unable to detect an encoding as iconv is; the difference is that the")
print("   claim is an argument here and a flag there.")

print()
print("3. //IGNORE AND //TRANSLIT, SPELLED AS errors=")
text = "a€b\n"  # a € b
for policy in ("strict", "ignore", "replace", "xmlcharrefreplace", "backslashreplace", "namereplace"):
    try:
        out = hx(text.encode("ascii", errors=policy))
    except UnicodeEncodeError as e:
        out = f"UnicodeEncodeError at byte {e.start}: {e.reason}"
    print(f"   errors={policy:<20} {out}")
print("   'strict' is plain iconv, 'ignore' is //IGNORE. There is no //TRANSLIT:")
print("   the closest is 'replace', which writes 3f — a question mark — and")
print("   never invents 'EUR'. Nothing in the standard library transliterates,")
print("   and that is a decision rather than a gap: what € becomes in ASCII is")
print("   a question about language, not about encoding.")

print()
print("4. WHERE PYTHON REFUSES AND ICONV DOES NOT")
cases = [
    ("plain ASCII", b"abc"),
    ("cafe + U+00E9", b"caf\xc3\xa9"),
    ("lone high byte", b"\xe9"),
    ("surrogate U+D800", b"\xed\xa0\x80"),
    ("overlong slash", b"\xc0\xaf"),
    ("U+10FFFF, the last", b"\xf4\x8f\xbf\xbf"),
    ("U+110000, one past", b"\xf4\x90\x80\x80"),
    ("f5: no code point", b"\xf5\x90\x80\x80"),
    ("five-byte sequence", b"\xfb\xbf\xbf\xbf\xbf"),
]
for label, raw in cases:
    try:
        raw.decode("utf-8")
        verdict = "accepted"
    except UnicodeDecodeError as e:
        verdict = f"refused: {e.reason}"
    print(f"   {label:<22} {hx(raw):<17} {verdict}")
print("   Compare the shell run. iconv agrees with Python on every classic")
print("   malformation and disagrees on the last three: it accepts them and")
print("   exits 0. The top of the code space is U+10FFFF — the highest number")
print("   UTF-16's surrogate pairs can express — and RFC 3629 restricted UTF-8")
print("   to the same ceiling in 2003. Those bytes name numbers above it, so")
print("   they are not code points at all; Python refuses them and Rust does")
print("   too (str::from_utf8 returns Utf8Error with valid_up_to 0 on all")
print("   three, and char::from_u32(0x110000) is None).")
