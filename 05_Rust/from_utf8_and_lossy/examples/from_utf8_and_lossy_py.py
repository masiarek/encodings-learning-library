"""The same six byte strings, decoded by Python — and the same byte offset.

Rust reports where the bytes stopped being text with `Utf8Error::valid_up_to()`.
Python reports it as `UnicodeDecodeError.start`. This program prints Python's
numbers for the identical inputs the Rust example uses, so the two keys can be
laid side by side.

Run:  python3 from_utf8_and_lossy_py.py
"""

import codecs

CASES = [
    ("valid", "café".encode()),
    ("Latin-1 é", b"caf\xe9 au"),
    ("cut mid-character", b"\xe0\xb2"),
    ("bad continuation", b"\xe0\xb2\x28"),
    ("surrogate, as UTF-8", b"\xed\xa0\x80"),
    ("three stray bytes", b"\x80\x80\x80"),
]


def hexs(b: bytes) -> str:
    return b.hex(" ")


def incomplete(b: bytes) -> bool:
    """True when the bytes are a valid PREFIX — more input could still fix them.

    This is Rust's `error_len() == None`, asked in Python's own words. The
    incremental decoder holds a partial sequence instead of raising, so
    final=False succeeding is exactly the verdict "not wrong yet".
    """
    try:
        codecs.getincrementaldecoder("utf-8")().decode(b, final=False)
        return True
    except UnicodeDecodeError:
        return False


print("1. THE SAME SIX INPUTS, AND THE SAME OFFSET")
print(f"   {'case':<21} {'bytes':<21} {'start':>7} {'end':>5} {'end-start':>10}")
for label, data in CASES:
    try:
        data.decode("utf-8")
        row = f"{'ok':>7} {'-':>5} {'-':>10}"
    except UnicodeDecodeError as exc:
        row = f"{exc.start:>7} {exc.end:>5} {exc.end - exc.start:>10}"
    print(f"   {label:<21} {hexs(data):<21} {row}")
print("   `start` is Rust's valid_up_to(), byte for byte, on every row. `end - start`")
print("   is Rust's error_len() on every row where Rust reports a number. Two languages,")
print("   two spellings, one measurement — because the measurement is a property of the")
print("   BYTES and not of whoever is reading them.")
print()

print("2. EXCEPT ON THE ROW WHERE RUST HAS A THIRD ANSWER")
print(f"   {'case':<21} {'bytes':<21} {'valid prefix?':>13}   what that means")
for label, data in CASES:
    try:
        data.decode("utf-8")
        verdict, meaning = "-", "already text"
        print(f"   {label:<21} {hexs(data):<21} {verdict:>13}   {meaning}")
        continue
    except UnicodeDecodeError:
        pass
    if incomplete(data):
        verdict, meaning = "yes", "INCOMPLETE — more bytes could still fix it"
    else:
        verdict, meaning = "no", "invalid — nothing appended makes this text"
    print(f"   {label:<21} {hexs(data):<21} {verdict:>13}   {meaning}")
print("   Rust puts that column in the return type: error_len() is None for the rows")
print("   marked yes and Some(n) for the rows marked no. Python's exception has no field")
print("   for it — `end` just runs to the end of the input — so the question has to be")
print("   asked of a different object, the incremental decoder, with final=False.")
print()

print("3. WHICH IS THE BUG A CHUNKED READ MAKES")
grin = "\U0001F600".encode()
print(f"   '\\U0001F600'.encode() = {hexs(grin)}   — four bytes, one character")
print(f"   {'split':<9} {'chunk 1':<12} {'chunk 2':<12} {'decode each':<16} incremental")
for cut in (1, 2, 3):
    head, tail = grin[:cut], grin[cut:]
    naive = []
    for part in (head, tail):
        try:
            part.decode("utf-8")
            naive.append("ok")
        except UnicodeDecodeError:
            naive.append("raises")
    dec = codecs.getincrementaldecoder("utf-8")()
    joined = dec.decode(head, final=False) + dec.decode(tail, final=True)
    print(f"   after {cut}   {hexs(head):<12} {hexs(tail):<12} {' / '.join(naive):<16} {joined!r}")
print("   BOTH halves raise, at every cut: one is a start byte with nothing after it,")
print("   the other is continuation bytes with nothing before them. That is what")
print("   `for chunk in f: chunk.decode()` meets at a read boundary. The last column is")
print("   an IncrementalDecoder holding the partial sequence until the rest arrives —")
print("   same bytes, and only one of the two columns is the file.")
print()

print("4. THE REPLACEMENT COUNT, WHICH BOTH LANGUAGES GET FROM THE SAME RULE")
print(f"   {'case':<21} {'bytes':<21} {'U+FFFD':>7}   result")
for label, data in CASES:
    lossy = data.decode("utf-8", errors="replace")
    print(f"   {label:<21} {hexs(data):<21} {lossy.count(chr(0xFFFD)):>7}   {lossy!r}")
print("   Compare that column against the Rust program's: identical on all six. Both")
print("   follow the Unicode Standard's recommendation of one U+FFFD per maximal")
print("   subpart, which is a recommendation and not a requirement — so this is a")
print("   measurement of two implementations agreeing, not a guarantee that any two do.")
print()

print("5. AND THE HANDLERS RUST DOES NOT SHIP")
data = b"caf\xe9 au"
for handler in ("strict", "replace", "ignore", "backslashreplace", "surrogateescape"):
    try:
        out = repr(data.decode("utf-8", errors=handler))
    except UnicodeDecodeError as exc:
        out = f"{type(exc).__name__} at byte {exc.start}"
    print(f"   errors={handler:<18} {out}")
print("   (Those are reprs, so backslashreplace's single backslash is shown doubled and")
print("   surrogateescape's parked byte is shown as the escape \\udce9 — printing that")
print("   string to a UTF-8 stream would raise — see 'Bytes that are not text'.)")
print("   Rust's std has the first two, under the names from_utf8 and from_utf8_lossy.")
print("   `ignore` and `backslashreplace` are a short loop over valid_up_to/error_len;")
print("   `surrogateescape` cannot be written at all, because the code points it parks")
print("   bytes in are the ones a Rust char is defined not to hold.")
