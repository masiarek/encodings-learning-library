"""Answer key: build an OSC 8 link by hand, and find the byte nobody escapes.

The escape sequence is printed with the ESC shown as \\x1b, never raw: a raw
escape in an answer key would be invisible in the diff that checks it.
"""
import urllib.parse

NAME = "café notes#1.txt"
DIR = "/home/ada/"

uri = "file://" + DIR + NAME
print(f"filename   {NAME!r}")
print(f"naive URI  {uri!r}")
print()
print("WHAT EACH ESCAPING RULE DOES TO IT")
rows = [
    ("quote(), default safe='/'", urllib.parse.quote(DIR + NAME)),
    ("quote() with nothing safe", urllib.parse.quote(DIR + NAME, safe="")),
    ("what a terminal usually emits", DIR + NAME.replace(" ", "%20").replace("#", "%23")),
]
for label, out in rows:
    print(f"   {label:<30} {out}")
print()
print("Look at the third row, which is what most tools actually write. The")
print("space and the '#' are percent-encoded, because they would end the URI")
print("or start a fragment. The 'é' is not. It is emitted as its raw UTF-8")
print("bytes, c3 a9, inside something declared to be a URI.")
print()
print("THE SEQUENCE, ASSEMBLED")
osc = "\x1b]8;;" + rows[2][1] + "\x1b\\" + NAME + "\x1b]8;;\x1b\\"
print(f"   {osc.encode('unicode_escape').decode()}")
print()
print("   \\x1b]8;;  starts the link and names the target")
print("   \\x1b\\     is ST, the string terminator")
print("   then the ordinary text the user sees, then an empty OSC 8 to close")
print()
print("   So a clickable filename is ordinary text with an escape sequence")
print("   wrapped round it. Nothing about the text changed -- which is why it")
print(f"   still measures {len(NAME)} characters to anything that strips escapes, and")
print(f"   {len(osc)} to anything that does not.")
print()
print("WHY THE ACCENT IS THE INTERESTING BYTE")
print("   RFC 3986 says a URI is a sequence of characters from a limited ASCII")
print("   set; anything else is percent-encoded UTF-8. By that rule the third")
print("   row is not a URI at all.")
print("   The OSC 8 specification does not require conformance either -- it")
print("   says the behaviour of non-ASCII bytes in the URI is UNDEFINED. So")
print("   every terminal is free to guess, and they do not all guess the same:")
print("   the link works in the emulator you tested and silently does nothing")
print("   in the next one.")
print()
print("   The safe thing to emit is the second row -- percent-encode")
print("   everything that is not unreserved, including the accent:")
print(f"   {urllib.parse.quote(NAME, safe='')}")
print("   It is uglier, it is a real URI, and it clicks everywhere.")

assert urllib.parse.quote("é", safe="") == "%C3%A9"
assert "\x1b]8;;" in osc
