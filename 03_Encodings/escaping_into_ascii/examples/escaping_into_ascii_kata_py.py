"""Answer key: one character through four ASCII-only channels.

Four schemes, four different answers, and -- the point of the kata -- four
different things being wrapped: code units, bytes, bytes-plus-a-charset-name,
and code points.
"""
import json
import urllib.parse

CH = "é"
EMOJI = "😀"

print(f"{'channel':<22} {'é':<24} what the scheme wraps")
print(f"{'JSON string':<22} {json.dumps(CH, ensure_ascii=True):<24} UTF-16 code units")
print(f"{'URL percent-encoding':<22} {urllib.parse.quote(CH):<24} BYTES -- of an unnamed encoding")
print(f"{'MIME encoded-word':<22} {'=?utf-8?q?=C3=A9?=':<24} bytes, of a charset it NAMES")
print(f"{'punycode (IDNA)':<22} {('caf' + CH).encode('idna').decode():<24} code points -- no bytes at all")
print()
print("THE SAME FOUR ON AN ASTRAL CHARACTER, WHERE THEY SEPARATE")
print(f"   JSON     {json.dumps(EMOJI, ensure_ascii=True)}   TWO escapes -- a surrogate pair, because")
print("                            \\u is a 16-bit code unit and nothing bigger")
print(f"   URL      {urllib.parse.quote(EMOJI)}   four bytes, four %XX, because UTF-8")
print("                            spells it in four -- and nothing in the URL")
print("                            says that it was UTF-8")
print()
print("WHY THE UNIT MATTERS MORE THAN THE SPELLING")
print()
print("JSON escapes CODE UNITS, so its escape hatch inherits UTF-16's shape --")
print("which is how a JSON document, whose transport is UTF-8 by RFC 8259, ends")
print("up containing a surrogate pair that has no UTF-8 encoding at all.")
print()
print("%XX escapes BYTES and never records whose. urllib defaults to UTF-8,")
print(f"but Latin-1 would give {urllib.parse.quote(CH, encoding='latin-1')} for the same character, and the URL is")
print("the same shape either way. The receiver has to be told out of band --")
print("which is why old query strings are a graveyard of guessed charsets.")
print()
print("A MIME encoded-word is the only one of the four that CARRIES the charset")
print("name inside the encoded text. That is why an email header can mix")
print("charsets word by word, and why it is the least ambiguous of the four.")
print()
print("Punycode does not touch bytes. It re-spells the sequence of CODE POINTS")
print("as ASCII letters using a delta-encoding, so it has no encoding")
print("parameter to get wrong -- and it is why an internationalized domain has")
print("an xn-- prefix rather than a percent sign.")
print()
print("So 'it is escaped' is not a description. Ask WHICH UNIT is escaped, and")
print("you have also asked which layer is allowed to decode it.")

assert json.dumps("é", ensure_ascii=True) == '"\\u00e9"'
assert urllib.parse.quote("é") == "%C3%A9"
