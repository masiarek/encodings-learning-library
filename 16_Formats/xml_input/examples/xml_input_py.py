#!/usr/bin/env python3
"""XML input: Ghidra's program-as-text -- a PROGRAM element with the
processor's byte order and width as attributes, a memory map whose
sections point at a sidecar .bytes file, and addresses as strings.

Builds the two files an export makes, in memory, and reads them the way
the loader does.

Run:  python3 xml_input_py.py
"""

import xml.etree.ElementTree as ET

BYTES = "café".encode() + b"\x00" + bytes.fromhex("55 48 89 e5 5d c3")

XML = """<?xml version="1.0" standalone="yes"?>
<?program_dtd version="1"?>
<PROGRAM NAME="hello.bin" EXE_PATH="/tmp/hello.bin" EXE_FORMAT="Raw Binary" IMAGE_BASE="08000000">
    <INFO_SOURCE TOOL="Ghidra 12.1.3" TIMESTAMP="Sat Sep 13 12:00:00 CEST 2026" />
    <PROCESSOR NAME="x86" ENDIAN="little" ADDRESS_MODEL="64-bit" LANGUAGE_PROVIDER="x86:LE:64:default:gcc" />
    <MEMORY_MAP>
        <MEMORY_SECTION NAME="ram" START_ADDR="08000000" LENGTH="12" PERMISSIONS="rwx">
            <MEMORY_CONTENTS FILE_NAME="hello.bin.bytes" FILE_OFFSET="0" />
        </MEMORY_SECTION>
    </MEMORY_MAP>
    <SYMBOL_TABLE>
        <SYMBOL ADDRESS="08000006" NAME="café_handler" TYPE="global" />
    </SYMBOL_TABLE>
    <COMMENTS>
        <COMMENT ADDRESS="08000000" TYPE="end-of-line">the string &quot;café&quot; &amp; a NUL</COMMENT>
    </COMMENTS>
</PROGRAM>
"""


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    root = ET.fromstring(XML.encode("utf-8"))

    section(1, "THE PROGRAM ELEMENT SAYS WHAT A HEADER WOULD")
    print(f"   {'attribute':<18} value")
    for k, v in root.attrib.items():
        print(f"   {k:<18} {v}")
    proc = root.find("PROCESSOR")
    for k, v in proc.attrib.items():
        print(f"   PROCESSOR/{k:<8} {v}")
    print()
    print("   ENDIAN and ADDRESS_MODEL are the two facts every binary header in")
    print("   this chapter encodes somewhere; here they are attribute strings,")
    print("   and the loader picks a language from them -- or from")
    print("   LANGUAGE_PROVIDER, which names it outright, if that is present.")
    print()

    section(2, "THE BYTES ARE NOT IN THE XML")
    sec = root.find("MEMORY_MAP/MEMORY_SECTION")
    contents = sec.find("MEMORY_CONTENTS")
    start = int(sec.get("START_ADDR"), 16)
    length = int(sec.get("LENGTH"))
    offset = int(contents.get("FILE_OFFSET"))
    sidecar = {"hello.bin.bytes": BYTES}
    data = sidecar[contents.get("FILE_NAME")][offset:offset + length]
    print(f"   MEMORY_SECTION {sec.get('NAME')!r}   START_ADDR {sec.get('START_ADDR')!r} -> {start:#x}   LENGTH {sec.get('LENGTH')!r} -> {length}")
    print(f"   MEMORY_CONTENTS FILE_NAME {contents.get('FILE_NAME')!r}   FILE_OFFSET {offset}")
    print(f"   the bytes, from the sidecar   {data.hex(' ')}")
    print()
    print("   An export is two files: the .xml and a .bytes beside it, named in")
    print("   FILE_NAME. The XML never holds a byte of the program; it holds")
    print("   where in the other file the bytes are, and where in memory they")
    print("   go. Import the .xml alone and the memory map is 0xff, by design.")
    print()

    section(3, "TWO NUMBERS, TWO BASES, AND THE TAG SAYS WHICH")
    for attr, value, how in (("START_ADDR", sec.get("START_ADDR"), "an address: hex, no prefix"), ("LENGTH", sec.get("LENGTH"), "a length: decimal"),
                             ("FILE_OFFSET", contents.get("FILE_OFFSET"), "an offset: decimal"), ("IMAGE_BASE", root.get("IMAGE_BASE"), "an address: hex")):
        as_hex, as_dec = int(value, 16), int(value) if value.isdigit() else None
        print(f"   {attr:<12} {value!r:<12} {how:<28} as hex {as_hex:<12} as decimal {as_dec}")
    print()
    print("   '12' is twelve as a LENGTH and eighteen as an address; '08000000'")
    print("   is 134,217,728 as an address and eight million as a length. The")
    print("   attribute name is the only thing that says which base to read a")
    print("   digit string in. Ghidra's XmlUtilities.parseInt reads decimal, or")
    print("   hex after a 0x prefix, so LENGTH=\"0x10\" is sixteen and \"10\" is ten;")
    print("   an address goes through the address factory, which reads hex bare.")
    print()

    section(4, "TEXT INSIDE TEXT IS ESCAPED, AND THE FILE'S ENCODING IS UTF-8 BY DEFAULT")
    comment = root.find("COMMENTS/COMMENT")
    symbol = root.find("SYMBOL_TABLE/SYMBOL")
    raw_line = next(l for l in XML.splitlines() if "<COMMENT " in l).strip()
    print(f"   in the file   {raw_line}")
    print(f"   parsed        {comment.text!r}")
    print(f"   symbol name   {symbol.get('NAME')!r}   {symbol.get('NAME').encode('utf-8').hex(' ')}")
    print()
    decl = XML.splitlines()[0]
    print(f"   declaration   {decl}")
    print("   no encoding= : XML 1.0 says UTF-8, or UTF-16 with a byte-order mark")
    for label, raw in (("UTF-8", XML.encode("utf-8")), ("UTF-16 with BOM", XML.encode("utf-16")), ("Latin-1, undeclared", XML.encode("latin-1"))):
        try:
            name = ET.fromstring(raw).find("SYMBOL_TABLE/SYMBOL").get("NAME")
            print(f"   {label:<22} parses, symbol {name!r}")
        except ET.ParseError:
            print(f"   {label:<22} ParseError: the bytes are not the encoding the declaration implies")
    print()
    print("   A quote is &quot; and an ampersand &amp;, so a comment can hold")
    print("   any character the encoding can. Without encoding= the parser")
    print("   assumes UTF-8, accepts UTF-16 because the BOM says so, and refuses")
    print("   a Latin-1 e9 as malformed -- the one case a binary header would")
    print("   have let through as a number.")


if __name__ == "__main__":
    main()
