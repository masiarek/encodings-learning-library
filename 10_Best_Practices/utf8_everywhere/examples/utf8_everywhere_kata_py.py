"""Answer key: five rules, and the line of code each one forbids."""
import unicodedata as ud

print("RULE 1 -- BYTES AT THE EDGES, TEXT IN THE MIDDLE")
print("   forbidden:  data = open(p, 'rb').read(); data.replace(b'a', b'b')")
print("               ...then treating data as text for the next 200 lines")
print("   Decode once, at the boundary. Everything inside works on str, and")
print("   the encode happens at the far edge. A program that carries bytes")
print("   through its middle has to remember an encoding at every step.")
print()
print("RULE 2 -- THE ENCODING COMES FROM THE PROTOCOL, NEVER FROM THE BYTES")
sample = "café".encode("utf-8")
print(f"   these bytes {sample.hex(' ')} are:")
for enc in ["utf-8", "latin-1", "cp1252"]:
    print(f"      valid {enc:<9} -> {sample.decode(enc)!r}")
print("   Three readings, all successful, one intended. Nothing in the file")
print("   says which. So the encoding is a fact about the CONTRACT -- the")
print("   Content-Type header, the database column, the interface spec -- and")
print("   guessing is what you do when the contract failed to say.")
print()
print("RULE 3 -- errors= IS A DECISION")
bad = b"caf\xe9"
for h in ["replace", "ignore", "surrogateescape"]:
    print(f"   {h:<16} {bad.decode('utf-8', h)!r}")
print("   Every one of those succeeded and every one of them means something")
print("   different about your data. Choosing by which one stops the traceback")
print("   is choosing at random.")
print()
print("RULE 4 -- NORMALIZE BEFORE COMPARING")
a, b = "café", "café"
print(f"   {a!r} == {b!r} -> {a == b}")
print(f"   after NFC      -> {ud.normalize('NFC', a) == ud.normalize('NFC', b)}")
print("   forbidden:  if user_input == stored_name:")
print("   ...on anything that came from a filesystem, a browser or a Mac.")
print()
print("RULE 5 -- 'LENGTH' HAS THREE ANSWERS, SO SAY WHICH")
for s in ["café", "😀", "é"]:
    print(f"   {s!r:<12} code points {len(s)}   utf-8 bytes {len(s.encode())}   "
          f"utf-16 units {len(s.encode('utf-16-le')) // 2}")
print("   forbidden:  VARCHAR(20) with no note about what 20 counts")
print("   A field limit, a truncation and a progress bar are three different")
print("   questions, and only one of them is about bytes.")
print()
print("THE RULES AS ONE SENTENCE")
print("   Decode at the door, work in text, encode at the far door, and write")
print("   the encoding down in the contract -- because the bytes will not")
print("   remember it for you and neither will the next person.")

assert b"caf\xe9".decode("latin-1") == "café"
assert ud.normalize("NFC", "café") == "café"
