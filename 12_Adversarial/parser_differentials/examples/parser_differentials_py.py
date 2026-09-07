#!/usr/bin/env python3
"""Two readers, one byte string: where a security check and the thing it guards
disagree about which characters the bytes spell.

Stdlib only. Every table used here (gbk, utf-7, latin-1) ships with Python.
"""


def hexs(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)


def read_as(b: bytes, table: str) -> str:
    try:
        s = b.decode(table)
    except UnicodeDecodeError as e:
        return f"invalid -- {e.reason}"
    cells = " ".join(c for c in s)
    return f"{len(s)} characters:  {cells}"


print("1. ONE BYTE STRING, THREE TABLES, THREE READINGS")
raw = b"\xbf\x5c\x27"
print(f"   the bytes            {hexs(raw)}")
for table in ("utf-8", "latin-1", "gbk"):
    print(f"   read as {table:<10}   {read_as(raw, table)}")
print("   Latin-1 reads three characters and one of them is a backslash.")
print("   GBK reads two, and the backslash is the SECOND HALF of the first one.")
print("   Nothing is corrupt. The bytes simply do not say how they should be cut.")
print()

print("2. THE ESCAPER THAT HANDS OVER THE QUOTE")


def addslashes(b: bytes) -> bytes:
    """Escape quotes by inserting 0x5C in front of them -- one byte at a time."""
    out = bytearray()
    for byte in b:
        if byte in (0x27, 0x22, 0x5C):
            out.append(0x5C)
        out.append(byte)
    return bytes(out)


sent = b"\xbf\x27"
escaped = addslashes(sent)
print(f"   attacker sends       {hexs(sent):<12} {len(sent)} bytes")
print(f"   the escaper sees     a quote (27) at offset 1, and puts 5C in front of it")
print(f"   the database gets    {hexs(escaped):<12} {len(escaped)} bytes")
print(f"   read as latin-1      {read_as(escaped, 'latin-1')}")
print(f"   read as gbk          {read_as(escaped, 'gbk')}")
print("   Under Latin-1 the quote is escaped, exactly as intended.")
print("   Under GBK the backslash was eaten as half of a character and the")
print("   quote came out live. The escaper never wrote a bug; it was reading")
print("   a different alphabet from the one the database was reading.")
print()
query = b"SELECT * FROM users WHERE name = '" + escaped + b"' AND admin = 0"
print(f"   the statement, as GBK characters:")
print(f"     {query.decode('gbk')}")
print("   The closing quote is now early, and everything after it is code.")
print()

print("3. THE PAGE THAT WAS NEVER LABELLED")
payload = b"+ADw-script+AD4-"
print(f"   payload bytes        {hexs(payload)}")
print(f"   as ASCII             {payload.decode('ascii')!r}")
print(f"   contains b'<script>' ? {b'<script>' in payload}")
print(f"   contains b'<' ?        {b'<' in payload}")
print(f"   decoded as utf-7     {payload.decode('utf-7')!r}")
print("   A filter looking for the eight bytes of '<script>' finds nothing --")
print("   nor does one looking for a bare '<', which is what most filters check,")
print("   because in UTF-7 those two characters are spelled +ADw- and +AD4-.")
print("   The tag does not exist until somebody decides the page is UTF-7 --")
print("   which a browser used to be willing to work out from the bytes alone.")
print()
print(f"   note: encoding is not forced to use the escape --")
print(f"   '<script>'.encode('utf-7') = {'<script>'.encode('utf-7')!r}")
print("   so the two spellings are not symmetric: an encoder picks one, and a")
print("   decoder must accept both. Every 'many spellings' bug lives in that gap.")
print()

print("4. THE SHAPE, WITHOUT THE STORY")
print("   Both cases are the same three lines:")
print("     stage A reads the bytes with table X  and says: nothing here")
print("     stage B reads the bytes with table Y  and acts on what it finds")
print("     the attacker chose the bytes so that X and Y disagree")
print("   So the question to ask of a pipeline is never 'is this input safe'.")
print("   It is: WHO DECODES, WITH WHICH TABLE, AND IN WHAT ORDER --")
print("   and the fix is to make the answer the same at every stage, once,")
print("   at the top, instead of letting each stage work it out for itself.")
