"""Answer key: six error policies, and what each one costs.

Every handler except strict succeeds. The kata is to say what each one threw
away and whether you could get it back.
"""
BAD = b"caf\xe9.txt"          # a Latin-1 é in a stream declared UTF-8
TEXT = "café → ż"

print("DECODING BYTES THAT ARE NOT UTF-8")
print(f"   input {BAD.hex(' ')}")
for h in ["strict", "replace", "ignore", "backslashreplace", "surrogateescape"]:
    try:
        got = BAD.decode("utf-8", h)
        back = None
        try:
            back = got.encode("utf-8", h)
        except UnicodeEncodeError:
            back = b"<cannot re-encode>"
        rev = "REVERSIBLE" if back == BAD else "lossy"
        print(f"   {h:<18} {got!r:<22} {rev}")
    except UnicodeDecodeError:
        print(f"   {h:<18} {'UnicodeDecodeError':<22} nothing produced -- an outage, on purpose")
print()
print("   Exactly one of the five is reversible, and it is the one that looks")
print("   strangest: surrogateescape maps each bad byte to a lone surrogate in")
print("   a private range, so the original byte can be recovered on the way")
print("   out. That is why it is what Python uses for FILENAMES, which are")
print("   bytes that must survive a round trip even when they are not text.")
print()
print("   ignore is silent data loss. replace is visible data loss -- U+FFFD is")
print("   a record that something was there, not of what. backslashreplace is")
print("   lossless as TEXT but the escape is now literal characters, so a later")
print("   consumer sees six characters where there was one byte.")
print()
print("ENCODING TEXT A TABLE CANNOT HOLD")
print(f"   text {TEXT!r} -> ascii")
for h in ["strict", "replace", "ignore", "backslashreplace", "xmlcharrefreplace", "namereplace"]:
    try:
        print(f"   {h:<18} {TEXT.encode('ascii', h)!r}")
    except UnicodeEncodeError:
        print(f"   {h:<18} UnicodeEncodeError")
print()
print("   Two of those exist only for encoding, and both are round-trippable by")
print("   a reader that knows the convention: xmlcharrefreplace produces valid")
print("   HTML/XML, namereplace produces Python source. Neither is 'safe' in")
print("   general -- they are safe for one consumer each.")
print()
print("THE DECISION, STATED PLAINLY")
print("   strict           an outage at 3am, and the only one that cannot")
print("                    silently ship wrong data")
print("   replace/ignore   a smaller or wronger value, and a green log")
print("   surrogateescape  a round trip, at the price of a str that is not")
print("                    encodable by anything else")
print("   The handler is not a convenience argument. It is where you write down")
print("   what your program should do when the world hands it something it")
print("   cannot explain -- and the default, strict, is a defensible answer.")

assert BAD.decode("utf-8", "surrogateescape").encode("utf-8", "surrogateescape") == BAD
assert BAD.decode("utf-8", "ignore") == "caf.txt"
