"""Answer key: nine ways out of one string, and the two bytes it will not carry.

The kata's claim to test is the page's: `surrogateescape` is reversible where
the other handlers are not, the reverse works on any ASCII-compatible codec
rather than only the one that made it, and the escape deliberately has no
spelling for the bytes the kernel reads.

Nothing here touches the filesystem, the locale or the clock. The page's own
`print(name)` row is environment-dependent on purpose and is exactly what an
answer key may not hold, so every value below is shown as hex or ascii().
"""
import json
import os

RAW = b"caf\xe9"                      # a Latin-1 e-acute in a stream declared UTF-8
NAME = RAW.decode("utf-8", "surrogateescape")

print(f"the bytes      {RAW.hex(' ')}")
print(f"the str        {ascii(NAME)}   len {len(NAME)}")
print()
print("PART ONE -- NINE WAYS OUT")
print()

WAYS = [
    ("encode('utf-8')", lambda: NAME.encode("utf-8")),
    ("encode('utf-8', 'surrogateescape')", lambda: NAME.encode("utf-8", "surrogateescape")),
    ("encode('latin-1', 'surrogateescape')", lambda: NAME.encode("latin-1", "surrogateescape")),
    ("encode('ascii', 'surrogateescape')", lambda: NAME.encode("ascii", "surrogateescape")),
    ("encode('utf-16-le', 'surrogateescape')", lambda: NAME.encode("utf-16-le", "surrogateescape")),
    ("encode('utf-8', 'surrogatepass')", lambda: NAME.encode("utf-8", "surrogatepass")),
    ("encode('utf-8', 'backslashreplace')", lambda: NAME.encode("utf-8", "backslashreplace")),
    ("encode('utf-8', 'replace')", lambda: NAME.encode("utf-8", "replace")),
    ("encode('utf-8', 'ignore')", lambda: NAME.encode("utf-8", "ignore")),
]

for label, fn in WAYS:
    try:
        out = fn()
    except UnicodeError as exc:
        print(f"   {label:<40} {type(exc).__name__}")
        continue
    verdict = "the bytes back" if out == RAW else "something else"
    print(f"   {label:<40} {len(out)} bytes  {out.hex(' '):<26} {verdict}")

print("""
   Three give the bytes back and they use three different codecs, which
   is the first answer: on the way OUT the handler does the work, not
   the codec. `ascii` cannot represent U+DCE9 and returns 0xE9 anyway.

   utf-16-le is the one that breaks the pattern, and PEP 383 says why in
   a sentence -- "encodings that are not compatible with ASCII are not
   supported by this specification". The escape is defined over bytes,
   and UTF-16's unit is two of them.

   Then the two that succeed and lie. `surrogatepass` writes SIX bytes,
   encoding the surrogate itself rather than putting the byte back, and
   `replace` writes FOUR -- the right length, the wrong file. 63 61 66
   3f is `caf?`, which is the same size as the answer, printable, and
   past any check that counts. `ignore` at least gets shorter.""")

print()
print("PART TWO -- WHICH BYTES CAN THE ESCAPE CARRY?")
print()
for cp in (0xDC00, 0xDC2F, 0xDC7F, 0xDC80, 0xDCE9, 0xDCFF):
    would_be = cp - 0xDC00
    try:
        out = chr(cp).encode("utf-8", "surrogateescape")
        print(f"   U+{cp:04X}  would be byte {would_be:#04x}   -> {out.hex()}")
    except UnicodeError as exc:
        print(f"   U+{cp:04X}  would be byte {would_be:#04x}   -> {type(exc).__name__}")

print("""
   The arithmetic is U+DC00 + byte, so the obvious guess is that all 256
   have a spelling. Half of them do not: the escape starts at DC80, and
   everything below is refused.

   Bytes under 128 are ASCII: they decode correctly, so they never need
   an escape, and giving them one would only build a way to smuggle
   them. Two of the refusals show what that would cost. Byte 0x2f is `/`
   and byte 0x00 is NUL -- the only two bytes a POSIX filename may not
   contain -- so a handler with a spelling for them would let a decoded
   name become a path the caller never wrote.""")

print()
print("PART THREE -- WHERE DID THIS STR COME FROM?")
print()
BY_HANDLER = RAW.decode("utf-8", "surrogateescape")
BY_HAND = "caf\udce9"
BY_JSON = json.loads('"caf\\udce9"')
print(f"   made by the handler   {ascii(BY_HANDLER)}")
print(f"   typed as a literal    {ascii(BY_HAND)}")
print(f"   parsed out of JSON    {ascii(BY_JSON)}")
print(f"   all three equal       {BY_HANDLER == BY_HAND == BY_JSON}")
print(f"   fsencode(the JSON one) == the original bytes   {os.fsencode(BY_JSON) == RAW}")
print("""
   One object, three provenances, no way to tell them apart -- a str
   keeps no record of which handler made it, and `==` was never going to
   say otherwise. That is the page's finding turned into the question a
   reviewer should ask: the last line is a byte reaching the kernel that
   appeared nowhere in the document it was parsed from.

   So the answer to "which of the three is safe" is none of them, and
   the question is the wrong one. What is safe is validating the name
   you parsed rather than the one you print.""")

print()
print("PART FOUR -- ONE CHARACTER IN, THREE OUT, AND NOTHING RAISED")
print()
ONE = "\udce9"
MID = ONE.encode("utf-8", "surrogatepass")
BACK = MID.decode("utf-8", "surrogateescape")
print(f"   {'start':<36} {ascii(ONE):<26} {len(ONE)} character")
print(f"   {'.encode(utf-8, surrogatepass)':<36} {MID.hex(' '):<26} {len(MID)} bytes")
print(f"   {'.decode(utf-8, surrogateescape)':<36} {ascii(BACK):<26} {len(BACK)} characters")
print(f"   {'.encode(utf-8, surrogateescape)':<36} "
      f"{BACK.encode('utf-8', 'surrogateescape').hex(' '):<26} "
      f"back to the same bytes: {BACK.encode('utf-8', 'surrogateescape') == MID}")
print("""
   Every step succeeded and the bytes still reverse, which is why this
   one is hard to catch: neither handler is wrong on its own. But they
   were asked opposite questions. `surrogatepass` wrote the surrogate
   AS a character, three bytes of UTF-8; `surrogateescape` read those
   three bytes as three undecodable bytes and escaped each one. Length
   1 became length 3, with no exception and no warning anywhere.

   The rule this leaves you with is the page's, stated as an operation
   rather than a fact: the handler is part of the format. Write down
   which one made the bytes, because the str will not remember, and
   `sys.getfilesystemencodeerrors()` only tells you which one the
   PLATFORM would have used.""")
