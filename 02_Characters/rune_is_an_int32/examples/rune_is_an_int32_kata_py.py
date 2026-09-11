"""Five fields, cut to fit -- the answers to the kata on the page.

A form keeps names in a fixed-width byte field and cuts whatever does not fit.
Each value below is what came back. The questions: how many U+FFFD does
Python's decode(..., 'replace') write, what is the len() of the result, and
what does Go's utf8.RuneCountInString say?

Go's number is computed from the mistakes Python's own decoder reports. Go's
documentation says RuneCountInString treats "erroneous and short encodings" as
single runes of width 1 byte, so it is the characters that decoded plus the
total LENGTH of the mistakes. The page checks that rule against Go itself.

Run:  python3 rune_is_an_int32_kata_py.py
"""

import codecs

REPLACEMENT = chr(0xFFFD)
LIMIT = 4

_lengths: list[int] = []


def _record(exc: UnicodeDecodeError) -> tuple[str, int]:
    _lengths.append(exc.end - exc.start)
    return (REPLACEMENT, exc.end)


codecs.register_error("rune_is_an_int32_kata.record", _record)

# Glyphs go last on every printed row: 😀 and 日本 are two columns wide each.
FIELDS = [
    (b"caf\xc3", "café, cut inside the é"),
    (b"5 \xe2\x82", "5 €, cut inside the €"),
    (b"hi \xf0\x9f\x98", "hi 😀, cut inside the 😀"),
    (b"\xc5\xbc\xc3\xb3\xc5", "żółw, cut inside the ł"),
    (b"\xe6\x97\xa5\xe6\x9c", "日本, cut inside the 本"),
]

rows = []
for data, what in FIELDS:
    _lengths.clear()
    text = data.decode("utf-8", "rune_is_an_int32_kata.record")
    assert text == data.decode("utf-8", "replace")
    lengths = list(_lengths)
    go_runes = len(text) - len(lengths) + sum(lengths)
    rows.append((data, what, text.count(REPLACEMENT), len(text), go_runes, lengths))

print("PART ONE -- FIVE FIELDS")
print("-" * 72)
print()
print(f"   {'the bytes that came back':<26} {'U+FFFD':>6} {'len()':>6} {'Go runes':>9}   what it was")
for data, what, markers, length, go, _ in rows:
    print(f"   {data.hex(' '):<26} {markers:>6} {length:>6} {go:>9}   {what}")
print()
print("   Every field holds exactly ONE mistake, so Python writes one U+FFFD each")
print("   time and len() counts it as one character. Go counts the same mistake as")
print("   one rune per byte it spans:")
print()
for data, what, markers, length, go, lengths in rows:
    kept = lengths[0]
    plural = "byte " if kept == 1 else "bytes"
    print(f"      the mistake is {kept} {plural} long   Go's count is {go - length:+d}   {what}")
print()
print("   So the two lengths agree on exactly the fields cut ONE byte into a")
print("   character -- café and żółw -- and everywhere else Go's is longer by the")
print("   bytes that were kept, minus one.")
print()

print("PART TWO -- THE FRONT END AND THE BACK END")
print("-" * 72)
print()
print(f"   A Go front end refuses anything over {LIMIT} runes. A Python back end")
print("   stores whatever it is given, and would call it len() characters long.")
print()
print(f"   refused by Go, yet {LIMIT} characters or fewer to Python:")
refused = [r for r in rows if r[4] > LIMIT and r[3] <= LIMIT]
for data, what, markers, length, go, _ in refused:
    print(f"      {go} runes to Go, {length} characters to Python   {what}")
print()
print(f"   {len(refused)} of the {len(rows)} fields. Not an exotic input: many fixed-width fields cut")
print("   a value to their byte width rather than refuse it, and here that leaves")
print("   the two services disagreeing about whether the value is too long.")
print("   Neither has misread a byte -- they found the same mistake and counted it")
print("   by different rules. A limit that crosses a language has to say what it")
print("   counts, and whether it counts before or after the bytes are decoded.")
print()

print("PART THREE -- THE RULE, FROM THE BYTES ALONE")
print("-" * 72)
print()
print("   Find where the field was cut. If the last character kept only its first")
print("   byte, the mistake is one byte long, and one byte is one marker under any")
print("   policy. If it kept two or more of its bytes, Go counts every one of them")
print("   and Python counts the mistake once: the difference is the bytes kept,")
print("   minus one. The bytes after the cut do not matter -- they are gone.")
