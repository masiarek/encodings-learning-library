"""Answer key: one byte string, two readers, and the gap between them."""
import json

print("1. THE SAME BYTES, TWO ALPHABETS")
raw = b"caf\xe9"
for enc in ["latin-1", "cp1252", "utf-8"]:
    try:
        print(f"   as {enc:<9} {raw.decode(enc)!r}")
    except UnicodeDecodeError:
        print(f"   as {enc:<9} UnicodeDecodeError -- refuses")
print("   Nothing in the bytes says which. A checker that decodes one way and")
print("   an actor that decodes another are looking at different strings.")
print()
print("2. THE CLASSIC: A CHECK IN BYTES, AN ACTION IN CHARACTERS")
payload = b"\xc0\xaf"                       # overlong '/'
print(f"   filter looks for the byte 2f in {payload.hex(' ')} -> "
      f"{'FOUND' if b'\\x2f' in payload else 'not found, passes'}")
try:
    payload.decode("utf-8")
except UnicodeDecodeError:
    print("   a STRICT decoder refuses this outright")
print("   a LENIENT decoder that assembles the payload bits yields "
      f"{chr(((payload[0] & 0x1F) << 6) | (payload[1] & 0x3F))!r}")
print("   Two components, one input, opposite conclusions. The check passed")
print("   because it was true about the bytes; the action happened because it")
print("   was true about the characters.")
print()
print("3. A JSON DIFFERENTIAL YOU CAN RUN TODAY")
doc = '{"role": "user", "role": "admin"}'
print(f"   {doc}")
print(f"   Python json.loads -> {json.loads(doc)}")
print("   Duplicate keys are not an error in the JSON spec; it says nothing")
print("   about which wins. Python keeps the LAST. Other parsers keep the")
print("   first. A gateway that validates with one library and a service that")
print("   acts with another can disagree about a single request -- and neither")
print("   is violating the specification.")
print()
print("4. AND ONE MORE, IN THE SAME LIBRARY")
print(r'   json.loads(\'"\ud800"\') accepts a lone surrogate: ' +
      repr(json.loads('"\\ud800"')))
try:
    json.loads('"\\ud800"').encode("utf-8")
except UnicodeEncodeError:
    print("   ...and the resulting str cannot be encoded as UTF-8 at all")
print("   So a document that parses is not a document that can be re-emitted")
print("   in the encoding its own RFC requires.")
print()
print("THE DEFENCE")
print("   One parser. If the checking stage and the acting stage cannot share")
print("   an implementation, they must share a CANONICAL FORM: parse once,")
print("   re-serialise, and pass the re-serialised value on -- so the second")
print("   stage never sees the attacker's spelling, only yours.")

assert b"\x2f" not in b"\xc0\xaf"
assert json.loads('{"a": 1, "a": 2}') == {"a": 2}
