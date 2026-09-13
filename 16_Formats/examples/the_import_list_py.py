#!/usr/bin/env python3
"""The twenty-four formats on Ghidra's import list, and the bytes each one
asks a loader to look at first.

The table is the chapter's summary. Each row's bytes are the ones the
format's own page builds and parses; this program only lines them up and
asks one question of each: is the signature something a person can read?

Run:  python3 the_import_list_py.py
"""

# (list name, where the signature sits, the bytes, how the loader recognises it)
FORMATS = [
    ("Android APK", "0 (and the last 22)", b"PK\x03\x04", "ZIP; classes.dex inside"),
    ("COFF", "0", b"\x4c\x01", "a machine type the table knows"),
    ("DEX", "0", b"dex\n035\x00", "magic"),
    ("DBG", "0", b"DI", "magic"),
    ("Dump File Loader", "0", b"MDMP", "one of four words"),
    ("DYLD Shared Cache", "0", b"dyld_v1 x86_64h\x00", "a 16-byte text field"),
    ("ELF", "0", b"\x7fELF", "magic"),
    ("GDT", "6", b"\x2e\x30\x21\x26\x34\xe9\x2c\x20", "magic, and the .gdt name"),
    ("GZF", "6", b"\x2e\x30\x21\x26\x34\xe9\x2c\x20", "magic, and the .gzf name"),
    ("GZT", "6", b"\x2e\x30\x21\x26\x34\xe9\x2c\x20", "magic, and the .gzt name"),
    ("Intel Hex", "0", b":", "a regex over the first line"),
    ("Java Class File", "0", b"\xca\xfe\xba\xbe", "magic"),
    ("Mach-O", "0", b"\xcf\xfa\xed\xfe", "one of four magics, or a fat header"),
    ("DEF", "-", b"", "the .def name, and one export"),
    ("Motorola Hex", "0", b"S", "the same regex as Intel Hex"),
    ("NE", "e_lfanew", b"NE", "MZ first, then this"),
    ("MZ", "0", b"MZ", "magic, and no NE or PE behind it"),
    ("PE", "e_lfanew", b"PE\x00\x00", "MZ first, then this"),
    ("PEF", "0", b"Joy!peff", "two tags"),
    ("MAP", "-", b"", "the .map name, and a symbol line"),
    ("Raw Binary", "-", b"", "nothing: every file qualifies"),
    ("OMF", "0", b"\x80", "a THEADR or LHEADR record"),
    ("XML Input Format", "-", b"", "parses as a PROGRAM element"),
    ("SARIF Input Format", "-", b"", "parses as SARIF"),
]


def printable(b):
    """The signature as a person reads it in a dump's text column."""
    if not b:
        return "-"
    if all(32 <= c < 127 for c in b):
        return b.decode("ascii")
    if all(32 <= c < 127 or c in (0, 10) for c in b):
        return b.decode("ascii").replace("\x00", "\\0").replace("\n", "\\n")
    return "(not text)"


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "THE BYTES A LOADER LOOKS AT FIRST")
    print(f"   {'format':<20} {'at':<20} {'bytes':<48} {'reads as':<20} recognised by")
    print()
    for name, where, sig, how in FORMATS:
        print(f"   {name:<20} {where:<20} {sig.hex(' '):<48} {printable(sig):<20} {how}")
    print()

    section(2, "COUNTED")
    with_sig = [f for f in FORMATS if f[2]]
    readable = [f for f in with_sig if printable(f[2]) not in ("(not text)", "-")]
    at_zero = [f for f in with_sig if f[1].startswith("0")]
    print(f"   formats on the list                     {len(FORMATS)}")
    print(f"   with a signature in the file            {len(with_sig)}")
    print(f"   ...of which the signature is text        {len(readable)}")
    print(f"   ...of which it sits at offset 0          {len(at_zero)}")
    print(f"   ...of which it sits somewhere else       {len(with_sig) - len(at_zero)}")
    print(f"   with no signature at all                {len(FORMATS) - len(with_sig)}")
    print()
    print("   A magic number is a number to the program and a picture to the")
    print("   person reading the dump, and most of these were chosen so the")
    print("   picture reads as a word. The ELF designers went one better: a")
    print("   first byte no text file can start with, then the name.")


if __name__ == "__main__":
    main()
