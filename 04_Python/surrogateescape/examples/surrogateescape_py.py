#!/usr/bin/env python3
"""One undecodable byte, carried through a str and put back unchanged.

Nothing here touches the filesystem. That is not only the repo's determinism
rule: macOS refuses to create a filename that is not valid UTF-8 at all, so the
file this page is about cannot exist on the machine most likely to run it.
The bytes are therefore written out by hand, which is what a directory read
would have handed us anyway."""

import codecs
import io
import json
import os
import sys
import textwrap

RULE = "-" * 72
W = 45  # label column: the widest call below is 44 characters

# What os.listdir() would have returned on a Linux box with an old file on it:
# "cafe au lait" with the e-acute written in Latin-1, so it is the byte 0xE9.
RAW = b"caf\xe9 au lait"


def cps(s):
    """A string as its code points, the way a bug report should quote it."""
    return " ".join("U+%04X" % ord(c) for c in s)


def wrapped(text, indent):
    """A verbatim message, folded to the page rather than truncated."""
    return textwrap.fill(text, width=72, initial_indent=indent,
                         subsequent_indent=indent + "  ")


def attempt(label, fn):
    """Run it, and show either the answer or the exception's own words.

    A UnicodeError's message is quoted exactly -- every word of it is a clue --
    so it is folded onto continuation lines instead of running off the page."""
    try:
        return "%-*s %s" % (W, label, ascii(fn()))
    except UnicodeError as exc:
        return label + "\n" + wrapped("%s: %s" % (type(exc).__name__, exc), " " * 7)


print("1. THE BYTE THAT IS NOT TEXT")
print(RULE)
print("   A POSIX filename is any bytes except NUL and '/'. It is not")
print("   required to be UTF-8, and on a disk that has been around a while")
print("   some of it will not be. Here is one, twelve bytes:")
print()
print("     %s" % RAW)
print("     %s" % " ".join("%02x" % b for b in RAW))
print()
print("   Python 3 hands you filenames as str, so somebody has to decode it,")
print("   and the honest answer is that it cannot be done:")
print()
print("     " + attempt("RAW.decode('utf-8')", lambda: RAW.decode("utf-8")))
print()
print("   That is correct and it is useless. The file exists, it has a name,")
print("   and a program that raises here cannot rename it, delete it, or")
print("   even finish listing the directory it sits in.")
print()

print("2. THE MAPPING")
print(RULE)
escaped = RAW.decode("utf-8", "surrogateescape")
print("     " + attempt("RAW.decode('utf-8','surrogateescape')", lambda: escaped))
print()
print("   len(escaped) = %d, the same as the byte count, and the fourth" % len(escaped))
print("   position now holds one code point that is not a character:")
print()
print("     %s" % cps(escaped))
print()
print("   PEP 383 puts every undecodable byte at U+DC00 + byte:")
print()
print("     byte  code point")
for b in (0x80, 0xC3, 0xE9, 0xFF):
    print("     0x%02X  %s" % (b, cps(bytes([b]).decode("utf-8", "surrogateescape"))))
print("     ...")
same = all(bytes([b]).decode("utf-8", "surrogateescape") == chr(0xDC00 + b)
           for b in range(0x80, 0x100))
print("     every byte 0x80..0xFF lands on U+DC00+byte:  %s" % same)
print()
print("   So the escape occupies exactly 128 code points, U+DC80..U+DCFF,")
print("   one for each byte that could ever need one.")
print()

print("3. AND BYTES BELOW 0x80 ARE REFUSED, ON PURPOSE")
print(RULE)
print("   The handler is an ordinary object, so you can ask it directly.")
print("   Hand it a failure over an ASCII byte and it declines to escape it,")
print("   re-raising the error it was called to fix:")
print()
handler = codecs.lookup_error("surrogateescape")
for raw in (b"\x41", b"\x7f", b"\x80", b"\xff"):
    exc = UnicodeDecodeError("utf-8", raw, 0, 1, "invalid start byte")
    label = "handler(error over byte 0x%02X)" % raw[0]
    print("     " + attempt(label, lambda e=exc: handler(e)))
print()
print("   PEP 383 states the reason: smuggled bytes would be a security risk")
print("   when the target system reads them as characters, 'such as path name")
print("   separators', so the PEP rejects smuggling bytes below 128. '/' is")
print("   0x2F and NUL is 0x00; the escape deliberately has no spelling for")
print("   the bytes that mean something to the kernel.")
print()

print("4. WHY A SURROGATE")
print(RULE)
print("   The range has to be one that correctly decoded text can never")
print("   contain, or the escape would collide with somebody's real data.")
print("   U+DC80..U+DCFF are unpaired low surrogates: reserved by Unicode for")
print("   UTF-16's pairing arithmetic, never assigned to a character, and not")
print("   encodable by any UTF at all --")
print()
print("     " + attempt("chr(0xDCE9).encode('utf-8')", lambda: chr(0xDCE9).encode("utf-8")))
print("     " + attempt("chr(0xDCE9).encode('utf-16-le')", lambda: chr(0xDCE9).encode("utf-16-le")))
print()
print("   -- which is exactly the property being borrowed. No decode of valid")
print("   input can produce one, so a str holding one has been through this")
print("   handler. The idea is Markus Kuhn's, who called it UTF-8b; PEP 383")
print("   credits him and is candid about what the argument does not cover:")
print("   'Data obtained from other sources may conflict with data produced")
print("   by this PEP. Dealing with such conflicts is out of scope of the")
print("   PEP.' Section 9 is what that sentence looks like in code.")
print()

print("5. THE ROUND TRIP, PROVED BY EXHAUSTION")
print(RULE)
print("   The claim is not 'it usually works'. Every one of the 65,536")
print("   two-byte strings, valid UTF-8 or not, decodes and re-encodes to")
print("   itself:")
print()
failures = sum(1 for i in range(0x10000)
               if (lambda r: r.decode("utf-8", "surrogateescape")
                   .encode("utf-8", "surrogateescape") != r)(bytes([i >> 8, i & 0xFF])))
print("     round-trip failures over all 65,536 two-byte strings:  %d" % failures)
print()
print("   And through the two functions that apply the policy for you, over")
print("   every single byte a filename may contain:")
print()
bad = [b for b in range(256) if os.fsencode(os.fsdecode(bytes([b]))) != bytes([b])]
print("     os.fsencode(os.fsdecode(b)) != b, for b in 0..255:     %d" % len(bad))
print()
print("     sys.getfilesystemencoding()       %r" % sys.getfilesystemencoding())
print("     sys.getfilesystemencodeerrors()   %r" % sys.getfilesystemencodeerrors())
print()
print("   Those two are what os.listdir(), open(), os.environ and sys.argv")
print("   already use on this system. You have been running this handler for")
print("   years without naming it.")
print()

print("6. surrogateescape IS NOT surrogatepass")
print(RULE)
print("   Two handlers one letter apart, one input, and the confusion is")
print("   expensive because both of them succeed:")
print()
print("     " + attempt("escaped.encode('utf-8','surrogateescape')",
                        lambda: escaped.encode("utf-8", "surrogateescape")))
print("     " + attempt("escaped.encode('utf-8','surrogatepass')",
                        lambda: escaped.encode("utf-8", "surrogatepass")))
print()
print("   surrogateescape puts the byte back: 12 bytes in, 12 bytes out.")
print("   surrogatepass encodes the surrogate ITSELF, as the three bytes")
print("   ED B3 A9 -- the spelling the WTF-8 specification gives an unpaired")
print("   surrogate, and not valid UTF-8 by any reading.")
print()
print("   Mix them and the length changes with no error anywhere:")
print()
wtf8 = escaped.encode("utf-8", "surrogatepass")
back = wtf8.decode("utf-8", "surrogatepass")
print("     surrogatepass out, surrogateescape back in:")
print("       %d bytes  ->  %d bytes" % (len(wtf8), len(back.encode("utf-8", "surrogateescape"))))
print("       and the two str values in between are equal:  %s" % (back == escaped))
print()
print("   That second line is the finding. The str keeps no record of which")
print("   handler made it, so one byte and three bytes become the same object")
print("   the moment they are inside.")
print()

print("7. WHERE IT LEAKS")
print(RULE)
print("   The escaped str is an ordinary str until something turns it back")
print("   into bytes without being told how:")
print()
print("     " + attempt("escaped.encode('utf-8')", lambda: escaped.encode("utf-8")))
print("     " + attempt("json.dumps(escaped).encode('utf-8')",
                        lambda: json.dumps(escaped, ensure_ascii=False).encode("utf-8")))
print()
print("   And it does not travel to every codec even when you do say the")
print("   handler's name. PEP 383: 'Encodings that are not compatible with")
print("   ASCII are not supported by this specification.'")
print()
for codec in ("ascii", "latin-1", "cp1252", "utf-8", "utf-16-le", "utf-32-le"):
    print("     " + attempt("escaped.encode(%r,'surrogateescape')" % codec,
                            lambda c=codec: escaped.encode(c, "surrogateescape")))
print()
print("   The four that work include 'ascii', which cannot represent the")
print("   character at all -- the handler returns the raw byte and the codec")
print("   passes it through. The two that fail are the ones whose own output")
print("   is code units, where a lone surrogate is illegal on the way out for")
print("   the same reason it is on the way in.")
print()
print("   Meanwhile every operation that stays inside str succeeds silently:")
print()
print("     " + attempt("len(escaped)", lambda: len(escaped)))
print("     " + attempt("escaped.upper()", lambda: escaped.upper()))
print("     " + attempt("escaped.startswith('caf')", lambda: escaped.startswith("caf")))
print("     " + attempt("escaped in {escaped: 1}", lambda: escaped in {escaped: 1}))
print("     " + attempt("json.dumps(escaped)", lambda: json.dumps(escaped)))
print()
print("   That last one is a JSON document containing \\udce9 -- syntactically")
print("   fine, accepted by json.loads, and impossible to write to a UTF-8")
print("   file. json.dumps did not fail; it deferred.")
print()

print("8. AND PRINTING IT DEPENDS ON THE LOCALE")
print(RULE)
print("   sys.stdout is a codec too, with an errors policy chosen at startup")
print("   from the environment. In this process:")
print()
print("     sys.stdout.encoding  %r" % sys.stdout.encoding)
print("     sys.stdout.errors    %r" % sys.stdout.errors)
print()
print("   Both configurations modelled over a buffer, which is all a text")
print("   stream is -- same string, same encoding, two error policies:")
print()
for errors in ("strict", "surrogateescape"):
    buf = io.BytesIO()
    stream = io.TextIOWrapper(buf, encoding="utf-8", errors=errors, newline="")
    try:
        stream.write(escaped)
        stream.flush()
        got = "wrote %d bytes, positions 3-4 are %s" % (
            len(buf.getvalue()),
            " ".join("%02x" % b for b in buf.getvalue()[3:5]))
    except UnicodeEncodeError as exc:
        got = None
        print("     errors=%s" % errors)
        print(wrapped("%s: %s" % (type(exc).__name__, exc), " " * 7))
    if got is not None:
        print("     errors=%-16s %s" % (errors, got))
print()
print("   So the same print() raises on a machine in a UTF-8 locale and puts")
print("   a raw 0xE9 on the terminal in the C locale, where Python switches")
print("   UTF-8 mode on and hands stdout this very handler. Neither is a bug")
print("   and there is no portable answer, so a program that has to SHOW one")
print("   of these names should ask for the shape it wants:")
print()
print("     " + attempt("escaped.encode('utf-8','backslashreplace')",
                        lambda: escaped.encode("utf-8", "backslashreplace")))
print()

print("9. THE ESCAPE IS NOT TAGGED")
print(RULE)
print("   Section 6 said the str keeps no record of where its surrogate came")
print("   from. Here is the consequence, in four lines with no error in them:")
print()
document = '"caf\\udce9 au lait"'
print("     JSON on the wire            %s" % document)
loaded = json.loads(document)
print("     json.loads gives            %s" % ascii(loaded))
print("     equal to our filename?      %s" % (loaded == escaped))
print("     os.fsencode(loaded)         %s" % ascii(os.fsencode(loaded)))
print()
print("   A JSON string may hold any \\uXXXX escape, unpaired surrogates")
print("   included, and Python's decoder accepts them. So anything that")
print("   parses JSON and then builds a path can write one arbitrary byte per")
print("   escape into a filename -- a byte that never appeared in the")
print("   document. This is the conflict PEP 383 put out of scope, and it is")
print("   yours: check the name you parsed, not the one you print.")
