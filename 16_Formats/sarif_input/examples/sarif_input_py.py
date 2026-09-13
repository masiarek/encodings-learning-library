#!/usr/bin/env python3
"""SARIF input: JSON, so an address is a number and a name is a string --
and JSON's number is whatever the reader makes of it, while its text must
be UTF-8 with no byte-order mark.

Run:  python3 sarif_input_py.py
"""

import json
import struct

ADDRESS = 0x7FFFFFFFFFFFFFF0          # a 64-bit address above 2**53


def sarif(address):
    """The shape Ghidra's SarifUtils.setLocation writes: a physicalLocation with an address object."""
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {"driver": {"name": "Ghidra", "version": "12.1.3"}},
            "results": [{
                "ruleId": "Symbols",
                "message": {"text": "café_handler \U0001F600"},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": "hello.bin"},
                        "address": {"absoluteAddress": address, "length": 16, "kind": "function",
                                    "name": "café_handler", "fullyQualifiedName": "ram"},
                    },
                    "logicalLocations": [{"index": 0}],
                }],
            }],
        }],
    }


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    doc = sarif(ADDRESS)

    section(1, "AN ADDRESS IS A JSON NUMBER")
    text = json.dumps(doc, ensure_ascii=False, indent=1)
    line = next(l for l in text.splitlines() if "absoluteAddress" in l).strip()
    print(f"   in the file   {line}")
    back = json.loads(text)["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["address"]["absoluteAddress"]
    print(f"   Python reads  {back}  = {back:#x}   exact: {back == ADDRESS}")
    print()
    print("   Ghidra writes address.getOffset(), a Java long, as a JSON number.")
    print("   Python's json reads a digit string with no fraction as an int, so")
    print("   the round trip here is exact -- but JSON itself has no integer type.")
    print()

    section(2, "WHAT A DOUBLE MAKES OF IT")
    for value in (2**53 - 1, 2**53, 2**53 + 1, ADDRESS, 0x7FFFFFFFFFFFFFFF):
        as_double = float(value)
        print(f"   {value:>20}  {value:#020x}   as float64 {int(as_double):>20}   {'exact' if int(as_double) == value else 'ROUNDED'}")
    print()
    print("   RFC 8259 says a reader that keeps numbers as IEEE doubles is")
    print("   interoperable up to 2**53, and warns about the rest. JavaScript,")
    print("   most JSON libraries and every spreadsheet keep doubles: a 64-bit")
    print("   address above 9,007,199,254,740,992 comes back a different number,")
    print("   with no error. Python and Java's Gson keep integers and do not.")
    print()

    section(3, "A NAME IS A STRING, AND ITS ESCAPES ARE UTF-16")
    name = doc["runs"][0]["results"][0]["message"]["text"]
    ascii_only = json.dumps(name)
    utf8 = json.dumps(name, ensure_ascii=False)
    print(f"   the text        {name!r}")
    print(f"   ensure_ascii    {ascii_only}")
    print(f"   as UTF-8        {utf8}")
    print(f"   both decode to the same string: {json.loads(ascii_only) == json.loads(utf8)}")
    print()
    print("   JSON's escape is \\uXXXX, four hex digits: a UTF-16 unit. An emoji")
    print("   is two of them, a surrogate pair written in ASCII, and a reader")
    print("   has to pair them up again. Or the writer emits the UTF-8 bytes")
    print("   directly, which the standard prefers and every reader accepts.")
    print()

    section(4, "THE FILE MUST BE UTF-8, AND A BOM MAY NOT BE WRITTEN")
    raw = text.encode("utf-8")
    cases = (("UTF-8 bytes", raw), ("UTF-8 bytes with a BOM", b"\xef\xbb\xbf" + raw), ("UTF-16 bytes", text.encode("utf-16")),
             ("a str starting with U+FEFF", chr(0xFEFF) + text))
    for label, data in cases:
        head = data[:6].hex(" ") if isinstance(data, bytes) else repr(data[:3])
        try:
            json.loads(data)
            verdict = "parses"
        except ValueError as e:
            verdict = f"refused: {type(e).__name__}"
        print(f"   {label:<28} {head:<20} {verdict}")
    print()
    print("   RFC 8259 section 8.1: JSON exchanged between systems MUST be UTF-8,")
    print("   a writer MUST NOT add a byte-order mark, and a reader MAY ignore")
    print("   one. Python's json.loads, given bytes, sniffs UTF-8, -16 and -32")
    print("   from the first four and strips a BOM; given a str that begins")
    print("   with U+FEFF it refuses, because a str has no encoding to sniff.")
    print()

    section(5, "WHAT GHIDRA LOOKS FOR")
    loc = doc["runs"][0]["results"][0]["locations"][0]["physicalLocation"]
    print(f"   version                {doc['version']!r}")
    print(f"   artifactLocation.uri   {loc['artifactLocation']['uri']!r}")
    print(f"   address.absoluteAddress {loc['address']['absoluteAddress']:#x}   address.fullyQualifiedName {loc['address']['fullyQualifiedName']!r}")
    print()
    print("   SarifUtils.locationToAddress reads absoluteAddress as the offset")
    print("   and fullyQualifiedName as the address space, 'ram' here; the loader")
    print("   needs the name to end in .sarif, or .json, and the file to parse")
    print("   as SARIF 2.1.0 with a Ghidra-shaped run inside it.")


if __name__ == "__main__":
    main()
