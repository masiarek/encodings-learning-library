#!/usr/bin/env python3
"""Four ways to write a character where only ASCII is allowed -- and the four
different things they escape.

A JSON string, a URL, an email header and a domain name are all channels that
carry ASCII and nothing else. Each got an escape scheme, each was designed by
different people at a different time, and they do not agree about what the
escape wraps: JSON escapes UTF-16 code units, percent-encoding escapes bytes
and never says of what, a MIME encoded-word escapes bytes of a charset it
names, and punycode escapes nothing at all -- it re-spells code points.

Knowing which layer you are looking at is the whole skill. A '%C3%83%C2%A9' is
not a strange character, it is one layer too many.

Run:  python3 escaping_into_ascii_py.py
"""

import base64
import email.header
import json
import urllib.parse

BAR = "-" * 72
WORD = "żółw"          # Polish for turtle: four letters, seven UTF-8 bytes
HOST = "żółw.pl"


def head(n, title):
    print(f"\n{n}. {title}\n{BAR}")


# ------------------------------------------------------------------ 1
head(1, "ONE WORD, FOUR CHANNELS, FOUR ANSWERS")
mime = email.header.Header(WORD, "utf-8").encode()
puny = HOST.encode("idna").decode("ascii")
print(f"   the text                {WORD!r}   {len(WORD)} characters")
print(f"   its UTF-8 bytes         {WORD.encode().hex(' ')}   {len(WORD.encode())} bytes")
print()
print(f"   in a JSON string        {json.dumps(WORD)}")
print(f"   in a URL                {urllib.parse.quote(WORD)}")
print(f"   in an email header      {mime}")
print(f"   in a domain name        {puny}")
print()
print("   Four channels that carry ASCII only, four schemes invented")
print("   separately to get the same four letters through them. None of the")
print("   four outputs shares a single character with any other, and that is")
print("   not cosmetic: they are escaping different things.")

# ------------------------------------------------------------------ 2
head(2, "JSON ESCAPES UTF-16 CODE UNITS -- IN A FORMAT THAT IS UTF-8")
s = "😀ż"
print(f"   json.dumps({s!r})")
print(f"     default              {json.dumps(s)}")
print(f"     ensure_ascii=False   {json.dumps(s, ensure_ascii=False)}")
print()
units = s.encode("utf-16-be")
print(f"   the same string as UTF-16BE   {units.hex(' ')}")
print(f"   escapes in the default form   {json.dumps(s).count(chr(92) + 'u')}")
print(f"   UTF-16 code units in it       {len(units) // 2}")
print()
print("   The same number, because they are the same thing. A JSON \\uXXXX is")
print("   one UTF-16 code unit, so a character above U+FFFF is written as a")
print("   SURROGATE PAIR -- \\ud83d\\ude00 for one emoji. JSON itself is UTF-8")
print("   by RFC 8259, which has no surrogates in it at all; the escape form")
print("   is the one place UTF-16 still leaks into a modern UTF-8 stack, and")
print("   it is there because JavaScript strings were UTF-16 in 1999.")
print()
print("   The leak has a sharp edge. Half a pair is valid JSON syntax:")
lone = json.loads('"' + chr(92) + 'ud83d"')
print(f"     json.loads('\"\\ud83d\"')  ->  {lone!r}   {len(lone)} character")
try:
    lone.encode("utf-8")
except UnicodeEncodeError as exc:
    print(f"     .encode('utf-8')        ->  UnicodeEncodeError: {exc.reason}")
print()
print("   So a parser accepts it, a str holds it, and the very next encode")
print("   raises -- a payload that is legal JSON and cannot be written to a")
print("   UTF-8 file. Reject lone surrogates at the parse boundary, not later.")

# ------------------------------------------------------------------ 3
head(3, "PERCENT-ENCODING ESCAPES BYTES, AND NEVER SAYS WHICH KIND")
print(f"   {'urllib.parse.quote(' + repr(WORD) + ')':<32}{urllib.parse.quote(WORD)}")
print(f"   {repr(WORD) + '.encode().hex()':<32}{WORD.encode().hex(' ')}")
print()
print("   Line up the two rows: %C5%BC%C3%B3%C5%82w is the hex dump with a %")
print("   in front of every byte, and the ASCII 'w' left alone because it did")
print("   not need one. A URL is bytes; the escape says nothing whatever about")
print("   which encoding produced them. RFC 3986 recommends UTF-8 for new")
print("   schemes and cannot enforce it, so a %F3 from a Latin-2 form is just")
print("   as well-formed and decodes to a different letter.")
print()
print("   Two details that cause real bugs:")
for call, value, note in (
    ("quote('a b')", urllib.parse.quote("a b"), "a path: space becomes %20"),
    ("quote_plus('a b')", urllib.parse.quote_plus("a b"), "a form field: space becomes +"),
    ("quote('a/b')", urllib.parse.quote("a/b"), "safe='/' by default, so a path survives"),
    ("quote('a/b', safe='')", urllib.parse.quote("a/b", safe=""), "for ONE path segment"),
):
    print(f"     {call:<23} {value:<6}  {note}")
print()
once = urllib.parse.quote(WORD)
twice = urllib.parse.quote(once)
print("   And the one that fills bug trackers -- escaping something already escaped:")
for label, value in (
    ("encoded once", once),
    ("encoded twice", twice),
    ("unquote(twice)", urllib.parse.unquote(twice)),
    ("unquote(unquote(twice))", urllib.parse.unquote(urllib.parse.unquote(twice))),
):
    print(f"     {label:<25} {value}")
print()
print("   The %25 is a percent sign that was itself escaped. One unquote")
print("   returns the string to its previous layer, not to text -- which is")
print("   why the fix is counting layers, not adding another unquote.")

# ------------------------------------------------------------------ 4
head(4, "A MIME ENCODED-WORD IS THE ONE THAT NAMES ITS CHARSET")
utf8_ew = email.header.Header(WORD, "utf-8").encode()
latin2 = WORD.encode("iso-8859-2")
latin2_ew = "=?iso-8859-2?B?" + base64.b64encode(latin2).decode("ascii") + "?="
print(f"   as utf-8        {utf8_ew}")
print(f"   as iso-8859-2   {latin2_ew}")
print()
print(f"   the payload is base64 of the bytes:  {WORD.encode().hex(' '):<22} (utf-8, {len(WORD.encode())} bytes)")
print(f"                                        {latin2.hex(' '):<22} (latin-2, {len(latin2)} bytes)")
print()
print("   =?charset?encoding?payload?= -- and the charset is IN the header,")
print("   which none of the other three schemes manage. That is why an email")
print("   subject in a code page nobody uses any more still decodes correctly")
print("   thirty years later, and a URL from the same era does not.")
print()
print("   Reading one back gives you bytes plus the name to decode them with:")
for raw, charset in email.header.decode_header(utf8_ew):
    print(f"     decode_header  ->  {raw!r}, {charset!r}")
    print(f"     raw.decode(charset)  ->  {raw.decode(charset)!r}")
print()
print("   'B' is base64 and 'Q' is quoted-printable, a Latin-1-flavoured cousin")
print("   of percent-encoding that uses = instead of %. The letter is")
print("   case-insensitive, which is why Python writes ?b? and most mail")
print("   clients write ?B?.")

# ------------------------------------------------------------------ 5
head(5, "PUNYCODE MOVES CODE POINTS, AND TOUCHES NO BYTES AT ALL")
print(f"   {HOST!r}.encode('idna')   {HOST.encode('idna').decode('ascii')}")
print(f"   {WORD!r}.encode('punycode')   {WORD.encode('punycode').decode('ascii')}")
print()
print("   Read the output: 'w-uga1v8h'. The 'w' is the one ASCII letter of")
print("   żółw, kept in place and in order; everything after the hyphen is a")
print("   base-36 description of which characters were removed and where they")
print("   go back. Nothing here is a byte -- punycode is defined over code")
print("   points, so there is no encoding to guess and no mojibake to have.")
print("   The 'xn--' prefix is what marks a label as encoded rather than a")
print("   domain that really is called that.")
print()
print("   IDNA normalises the label it has to encode, and passes an ASCII")
print("   label through untouched -- case included, since DNS ignores case:")
for variant in ("żółw.pl", "ŻÓŁW.pl", "Żółw.PL"):
    print(f"     {variant!r:<12} -> {variant.encode('idna').decode('ascii')}")
print()
print("   Normalising is not always harmless. The stdlib codec implements")
print("   IDNA2003, whose nameprep step rewrites \u00df as ss before encoding:")
print(f"     {chr(39) + 'stra\u00dfe.de' + chr(39) + '.encode(' + chr(39) + 'idna' + chr(39) + ')':<32}-> {'stra\u00dfe.de'.encode('idna').decode('ascii')}")
print(f"     {'the same name under IDNA2008':<32}-> {'xn--' + 'stra\u00dfe'.encode('punycode').decode('ascii')}.de")
print()
print("   Those are two different domains -- not two spellings of one. Under")
print("   IDNA2008 \u00df is a letter and survives into the label; under IDNA2003")
print("   it was a way of writing ss and does not. Python's built-in codec")
print("   gives the 2003 answer, the `idna` package on PyPI gives the 2008")
print("   one, and neither call site mentions a version.")

print()
print("   Which is the useful half and the dangerous half at once: two names")
print("   that a person cannot tell apart can still be two different domains,")
print("   because 'a' and the Cyrillic 'а' are different code points and")
print("   punycode preserves the difference perfectly.")

# ------------------------------------------------------------------ 6
head(6, "THE SAME FOUR LETTERS, SIX SIZES")
forms = [
    ("the text itself", WORD, "characters"),
    ("UTF-8 bytes", WORD.encode().hex(" "), "bytes"),
    ("JSON, ensure_ascii", json.dumps(WORD), "characters"),
    ("percent-encoded", urllib.parse.quote(WORD), "characters"),
    ("MIME encoded-word", utf8_ew, "characters"),
    ("punycode label", WORD.encode("punycode").decode("ascii"), "characters"),
]
for label, value, unit in forms:
    size = len(WORD.encode()) if unit == "bytes" else len(value)
    print(f"   {label:<22} {value:<34} {size:>2} {unit}")
print()
print("   A database column, a fixed-width field or a 63-character DNS label")
print("   is measured on ONE of those rows, and it is rarely the first. Ask")
print("   which layer the limit applies to before you size the field.")
