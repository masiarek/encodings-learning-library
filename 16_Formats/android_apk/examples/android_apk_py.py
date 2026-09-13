#!/usr/bin/env python3
"""Android APK: a ZIP read from its last 22 bytes, whose filenames are in
IBM code page 437 unless one bit in each header says UTF-8.

Builds a three-entry APK-shaped ZIP in memory with the standard library,
reads its end-of-central-directory record by hand, and then clears the
UTF-8 flag on a copy to watch a filename change code page.

Run:  python3 android_apk_py.py
"""

import io
import struct
import zipfile

EOCD = b"PK\x05\x06"
CENTRAL = b"PK\x01\x02"
LOCAL = b"PK\x03\x04"
UTF8_FLAG = 0x0800
STAMP = (1980, 1, 1, 0, 0, 0)          # the earliest date a ZIP can hold; fixed so the bytes never change


def build():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        z.writestr(zipfile.ZipInfo("classes.dex", STAMP), b"dex\n035\x00" + bytes(104))
        z.writestr(zipfile.ZipInfo("AndroidManifest.xml", STAMP), b"\x03\x00\x08\x00" + bytes(12))
        z.writestr(zipfile.ZipInfo("assets/café.txt", STAMP), "café\n".encode())
    return buf.getvalue()


def clear_utf8_flags(data):
    """Turn bit 11 off in every local and central header -- the file is then, by APPNOTE, CP437."""
    out = bytearray(data)
    pos = 0
    while True:
        pos = out.find(LOCAL, pos)
        if pos < 0:
            break
        (flags,) = struct.unpack_from("<H", out, pos + 6)
        struct.pack_into("<H", out, pos + 6, flags & ~UTF8_FLAG)
        pos += 4
    pos = 0
    while True:
        pos = out.find(CENTRAL, pos)
        if pos < 0:
            break
        (flags,) = struct.unpack_from("<H", out, pos + 8)
        struct.pack_into("<H", out, pos + 8, flags & ~UTF8_FLAG)
        pos += 4
    return bytes(out)


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    apk = build()

    section(1, "A ZIP IS READ FROM THE END")
    tail = apk[-22:]
    sig, disk, cd_disk, n_here, n_total, cd_size, cd_offset, comment_len = struct.unpack("<IHHHHIIH", tail)
    print(f"   file size {len(apk)}   last 22 bytes   {tail.hex(' ')}")
    print()
    print(f"   signature      {tail[:4]!r}   {sig:#010x}")
    print(f"   entries        {n_total}")
    print(f"   central dir    {cd_size} bytes at offset {cd_offset}")
    print(f"   comment        {comment_len} bytes")
    print()
    print(f"   offset 0        {apk[:4]!r}   a local file header -- the FIRST entry, not the index")
    print(f"   offset {cd_offset:<7}  {apk[cd_offset:cd_offset + 4]!r}   the central directory, which is the index")
    print()
    print("   A reader seeks to the end, finds this record, and follows its")
    print("   offset to the central directory; the local headers at the front")
    print("   are reached from there. PK\\3\\4 at offset 0 is what file(1) tests,")
    print("   and it is a convention, not what a ZIP reader uses.")
    print()

    section(2, "SO BYTES IN FRONT DO NOT BREAK IT")
    with zipfile.ZipFile(io.BytesIO(b"#!/bin/sh\nexec unzip $0\n" + apk)) as z:
        names = z.namelist()
    print(f"   24 bytes of shell script, then the ZIP   opens: {names}")
    try:
        with zipfile.ZipFile(io.BytesIO(apk + b"trailing junk")) as z:
            names = z.namelist()
        print(f"   the ZIP, then 13 bytes of junk           opens: {names}")
    except zipfile.BadZipFile:
        print("   the ZIP, then 13 bytes of junk           refused: BadZipFile")
    print()
    print("   Self-extracting archives and installers are exactly a program with")
    print("   a ZIP appended, and every reader that starts from the end handles")
    print("   them. The offsets inside are relative to the archive, so zipfile")
    print("   measures where the archive begins and corrects them.")
    print()

    section(3, "A FILENAME'S CODE PAGE IS ONE BIT IN ITS HEADER")
    pos = 0
    while (pos := apk.find(LOCAL, pos)) >= 0:
        flags, = struct.unpack_from("<H", apk, pos + 6)
        (nlen,) = struct.unpack_from("<H", apk, pos + 26)
        name = apk[pos + 30:pos + 30 + nlen]
        bit = "set  " if flags & UTF8_FLAG else "clear"
        print(f"   at {pos:<4} flags {flags:#06x}  bit 11 {bit}  name bytes {name.hex(' ')}")
        pos += 4
    print()
    with zipfile.ZipFile(io.BytesIO(apk)) as z:
        print(f"   zipfile reads   {z.namelist()}")
    with zipfile.ZipFile(io.BytesIO(clear_utf8_flags(apk))) as z:
        print(f"   bit 11 cleared  {z.namelist()}")
    print()
    print("   Same name bytes, 63 61 66 c3 a9, in both files. With bit 11 set")
    print("   they are UTF-8 and read back as café; with it clear the APPNOTE")
    print("   says IBM code page 437, and c3 a9 is two characters there. Python")
    print("   sets the bit only when a name is not ASCII, which is why the")
    print("   first two entries carry 0x0000: for ASCII the two tables agree.")
    print()

    section(4, "WHAT THE APK LOADER LOOKS FOR")
    with zipfile.ZipFile(io.BytesIO(apk)) as z:
        wanted = ["classes.dex"] + [f"classes{i}.dex" for i in range(2, 4)]
        for w in wanted:
            print(f"   /{w:<14} {'found' if w in z.namelist() else 'absent -- the loader stops here'}")
    print()
    print("   Ghidra asks the ZIP for /classes.dex, then /classes2.dex, and so on")
    print("   until one is missing, and loads each as a DEX program. Everything")
    print("   else in the archive -- the manifest, the resources, the signature")
    print("   block -- is a file it can list and does not read.")


if __name__ == "__main__":
    main()
