#!/usr/bin/env python3
"""The two arguments of .encode() and .decode(), and what the second one costs.

The first argument names a table. The second names a policy for the characters
or bytes that table cannot express -- and every policy except one throws
something away. This program is about which one, and how loudly."""

import codecs
import textwrap

RULE = "-" * 72

# One file that is not what it claims: "café au lait" written in Latin-1, so
# the e-acute is the single byte 0xE9 and the whole thing is invalid UTF-8.
BAD = b"caf\xe9 au lait"

# One string that Latin-1 cannot hold. A price is the honest example: the euro
# sign was added to Unicode in 1998 and to Windows-1252, and to no ISO 8859-1
# table anywhere -- which is how a legacy system meets it.
UNENCODABLE = "10 €"

BAD4 = b"caf\xe9"  # the short form, for the side-by-side in section 5


def show(label, fn, width=24):
    """Print a call's result, or the class of the exception it raised."""
    try:
        return "%-*s %s" % (width, label, ascii(fn()))
    except Exception as exc:
        return "%-*s %s" % (width, label, type(exc).__name__)


print("1. TWO ARGUMENTS, AND THE SECOND ONE HAS A DEFAULT")
print(RULE)
print("     bytes.decode(encoding, errors='strict')")
print("     str.encode(encoding, errors='strict')")
print()
print("   The first names a table. The second names what to do when the table")
print("   has no answer. Leaving it out is not neutrality -- it is a choice,")
print("   and the choice is to raise:")
print()
try:
    BAD.decode("utf-8")
except UnicodeDecodeError as bare:
    try:
        BAD.decode("utf-8", "strict")
    except UnicodeDecodeError as named:
        print("     .decode('utf-8') and .decode('utf-8','strict') raise the")
        print("     same exception with the same message:  %s" % (str(bare) == str(named)))
print()

print("2. THE EXCEPTION IS A REPORT, NOT A COMPLAINT")
print(RULE)
try:
    BAD.decode("utf-8")
except UnicodeDecodeError as exc:
    print("     " + str(exc))
    print()
    print("   Every clause of that sentence is an attribute you can read:")
    print()
    for attr, gloss in (("encoding", "the table that was asked"),
                        ("object", "the whole input, not just the bad part"),
                        ("start", "the offset where it went wrong"),
                        ("end", "and where the trouble stops"),
                        ("reason", "which rule was broken")):
        print("     .%-9s %-30s %s" % (attr, ascii(getattr(exc, attr)), gloss))
    print()
    print("     .object[.start:.end]  ->  %r" % exc.object[exc.start:exc.end])
    print()
    print("   So a handler for this does not have to guess. And the class is")
    print("   a ValueError, which is what a bare `except ValueError` catches:")
    print()
    print("     %s" % " -> ".join(c.__name__ for c in type(exc).__mro__[:4]))
print()
print("   Encoding fails the same way, with a different reason:")
print()
try:
    UNENCODABLE.encode("latin-1")
except UnicodeEncodeError as exc:
    print("     " + str(exc))
    print("     .reason is %s -- Latin-1 has 256 slots and no more," % ascii(exc.reason))
    print("     and this character's number is %d." % ord("€"))
print()

print("3. THE HANDLERS, BOTH DIRECTIONS")
print(RULE)
print("   Python registers eight by name. They are not interchangeable and")
print("   they are not symmetrical -- two of them do not work on decode at")
print("   all, and refuse with a TypeError rather than a UnicodeError:")
print()
HANDLERS = ["strict", "ignore", "replace", "backslashreplace",
            "xmlcharrefreplace", "namereplace", "surrogateescape", "surrogatepass"]
print("     %-18s %-24s %s" % ("handler", "decode utf-8 of", "encode latin-1 of"))
print("     %-18s %-24s %s" % ("", ascii(BAD), ascii(UNENCODABLE)))
print("     " + "-" * 66)
for h in HANDLERS:
    try:
        d = ascii(BAD.decode("utf-8", h))
    except Exception as exc:
        d = "! " + type(exc).__name__
    try:
        e = ascii(UNENCODABLE.encode("latin-1", h))
    except Exception as exc:
        e = "! " + type(exc).__name__
    print("     %-18s %-24s %s" % (h, d, e))
print()
print("   Three things to read off it. `xmlcharrefreplace` and `namereplace`")
print("   are ENCODE-ONLY: there is no sensible XML entity for a byte that is")
print("   not a character. `surrogatepass` fails BOTH columns here, because")
print("   it handles surrogate code points and neither of these inputs has")
print("   one -- it is not a general-purpose escape. And `surrogateescape`")
print("   works on the left and raises on the right, which is correct: it")
print("   only re-encodes the surrogates it made.")
print()

print("4. `replace` MEANS TWO DIFFERENT CHARACTERS")
print(RULE)
print("     decoding    " + ascii(BAD.decode("utf-8", "replace")))
print("     encoding    " + ascii(UNENCODABLE.encode("latin-1", "replace")))
print()
print("   U+FFFD REPLACEMENT CHARACTER on the way in; the ASCII question")
print("   mark, 0x3F, on the way out. One policy name, two markers, and only")
print("   one of them is rare enough in real text to grep for.")
print()

print("5. EVERY MARKER IS FORGEABLE")
print(RULE)
print("   This is the finding that decides which policy to use, and it is")
print("   easy to miss because each handler looks like it leaves a trace.")
print("   For each of the three lossy ones, here is an input containing NO")
print("   bad bytes at all that decodes to the identical string:")
print()
for h, innocent, what in [
        ("replace", "caf�".encode("utf-8"), "a real U+FFFD, which is a normal character"),
        ("backslashreplace", b"caf\\xe9", "the four ASCII characters \\ x e 9"),
        ("ignore", b"caf", "a file that simply says 'caf'")]:
    a = BAD4.decode("utf-8", h)
    b = innocent.decode("utf-8", h)
    print("     %s" % h)
    print("       %-22s -> %-14s  (four bytes, one bad)" % (ascii(BAD4), ascii(a)))
    print("       %-22s -> %-14s  identical: %s" % (ascii(innocent), ascii(b), a == b))
    print("       the second input is %s" % what)
print()
print("   So none of the three can be undone, and none of them can even be")
print("   DETECTED after the fact: a U+FFFD in your database might be a byte")
print("   somebody lost, or it might be what the user typed. The marker is")
print("   not a record of damage, it is a character.")
print()

print("6. THE ONE THAT IS REVERSIBLE")
print(RULE)
kept = BAD.decode("utf-8", "surrogateescape")
print("     decode surrogateescape   %s" % ascii(kept))
print("     encode it back           %s" % ascii(kept.encode("utf-8", "surrogateescape")))
print("     byte-identical to input  %s" % (kept.encode("utf-8", "surrogateescape") == BAD))
print()
print("   That is a whole page of its own -- how it works, where it leaks,")
print("   and the byte it lets a JSON document write into a filename.")
print()

print("7. HOW MUCH DID EACH ONE COST")
print(RULE)
mixed = b"caf\xe9 au lait, \xffour euros"
print("     input: %s  (%d bytes, two bad ones)" % (ascii(mixed), len(mixed)))
print()
print("     %-18s %-6s %-8s %-11s %s" % ("handler", "chars", "U+FFFD", "reversible", "can you tell?"))
print("     " + "-" * 60)
for h in ("ignore", "replace", "backslashreplace", "surrogateescape"):
    s = mixed.decode("utf-8", h)
    try:
        rev = s.encode("utf-8", h) == mixed
    except UnicodeError:
        rev = False
    tell = {"ignore": "no", "replace": "only by guessing",
            "backslashreplace": "only by guessing", "surrogateescape": "yes"}[h]
    print("     %-18s %-6d %-8d %-11s %s" % (h, len(s), s.count("�"), str(rev), tell))
print()
print("   `ignore` is the row to look at. The string got SHORTER and there")
print("   is nothing in it, or in any return value, that says so. That is")
print("   why it is the one policy this library tells you never to use: it")
print("   is not 'be lenient', it is 'delete evidence and report success'.")
print()

print("8. HOW MANY U+FFFD IS ALSO A DECISION")
print(RULE)
print("   `replace` does not write one marker per bad byte. It writes one")
print("   per maximal subpart -- the longest prefix that could still have")
print("   become a valid sequence:")
print()
print("     %-24s %-10s %s" % ("bytes", "bytes in", "U+FFFD out"))
for raw in (b"\xe9", b"\xf0\x9f", b"\xf0\x9f\x98", b"\xff\xff\xff", b"\xed\xa0\x80"):
    print("     %-24s %-10d %d" % (ascii(raw), len(raw), len(raw.decode("utf-8", "replace"))))
print()
print("   Two bytes of a truncated emoji are ONE marker: they are still a")
print("   plausible beginning. Three bytes of 0xFF are three, because none")
print("   of them could start anything. And the last row is the subtle one --")
print("   0xED IS a legal lead byte, but only in front of 0x80..0x9F, so")
print("   0xED 0xA0 is rejected at the SECOND byte and the maximal subpart")
print("   is just 0xED. That is the surrogate range being excluded, one")
print("   byte earlier than the arithmetic alone would suggest.")
print()

print("9. A POLICY YOU WRITE YOURSELF")
print(RULE)
print("   The eight names are just registered functions. A handler takes the")
print("   exception and returns (replacement, where to resume) -- so the")
print("   policy nobody ships, 'replace it AND tell me where', is four lines:")
print()
log = []


def audit(exc):
    log.append((exc.start, bytes(exc.object[exc.start:exc.end])))
    return ("�", exc.end)


codecs.register_error("audit", audit)
print("     text     %s" % ascii(mixed.decode("utf-8", "audit")))
print("     log      %s" % ascii(log))
print()
print("   Now the U+FFFD is not the only record, so section 5's ambiguity is")
print("   gone: the offsets and the original bytes are beside it.")
print()

print("10. THE FIRST ARGUMENT IS A NAME, AND NAMES HAVE ALIASES")
print(RULE)
print("   Six spellings of one codec, resolved through the registry:")
print()
for n in ("latin-1", "latin1", "iso-8859-1", "iso8859_1", "L1", "cp819"):
    print("     %-12s -> %s" % (n, codecs.lookup(n).name))
print()
print("   Note the canonical name is not any of the ones people type.")
print("   Whether two spellings are the same codec is a question for")
print("   codecs.lookup(), never for the eye.")
print()
print("   And the pair that looks like an alias and is not:")
print()
differ = [b for b in range(256)
          if bytes([b]).decode("cp1252", "replace") != bytes([b]).decode("latin-1")]
print("     bytes where cp1252 and latin-1 disagree:  %d of 256" % len(differ))
print("     the range:  0x%02X..0x%02X" % (differ[0], differ[-1]))
print("     0x80 is %s in cp1252 and %s in latin-1"
      % (ascii(b"\x80".decode("cp1252")), ascii(b"\x80".decode("latin-1"))))
print()
print("   Those 32 are the C1 control block, which Windows reused for the")
print("   euro sign and the smart quotes. A file decoded with the wrong one")
print("   of this pair is correct for 224 bytes out of 256.")
print()

print("11. NOT EVERY CODEC IS A TEXT CODEC")
print(RULE)
print("   The registry also holds transforms that are bytes-to-bytes or")
print("   str-to-str. .encode()/.decode() refuse them, by name, with a")
print("   message that tells you the right door:")
print()
for label, fn in (("b'abc'.decode('base64_codec')", lambda: b"abc".decode("base64_codec")),
                  ("'abc'.encode('rot13')", lambda: "abc".encode("rot13"))):
    try:
        print("     %-32s %s" % (label, ascii(fn())))
    except LookupError as exc:
        print("     %s" % label)
        print(textwrap.fill(str(exc), width=64, initial_indent=" " * 7,
                            subsequent_indent=" " * 9))
print()
for label, fn in (("codecs.encode('abc','rot13')", lambda: codecs.encode("abc", "rot13")),
                  ("codecs.decode(b'YWJj','base64_codec')", lambda: codecs.decode(b"YWJj", "base64_codec"))):
    print("     %-38s %s" % (label, ascii(fn())))
print()

print("12. THREE SPELLINGS, ONE OPERATION")
print(RULE)
good = "café".encode("utf-8")
print("     " + show("good.decode('utf-8')", lambda: good.decode("utf-8"), 34))
print("     " + show("str(good, 'utf-8')", lambda: str(good, "utf-8"), 34))
print("     " + show("codecs.decode(good, 'utf-8')", lambda: codecs.decode(good, "utf-8"), 34))
print()
print("     all three equal:  %s"
      % (good.decode("utf-8") == str(good, "utf-8") == codecs.decode(good, "utf-8")))
print()
print("   Prefer the method. `str(b, enc)` exists for symmetry with the other")
print("   constructors and reads as a cast rather than as a decision; and")
print("   `str(b)` with NO encoding does not decode at all -- it gives you")
print("   the repr, %s, which is a bug that runs." % ascii(str(good)))
