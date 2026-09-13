#!/usr/bin/env python3
"""DYLD shared cache: a 16-byte text magic naming the architecture, a
mapping table, and image records whose paths name libraries that no
longer exist as files.

Builds a small cache header with two mappings, two images and two
subcache entries, and reads it back the way Ghidra's DyldCacheHeader does.

Run:  python3 dyld_shared_cache_py.py
"""

import struct

# The twelve signatures Ghidra's DyldArchitecture knows, verbatim from its source at 12.1.3.
SIGNATURES = ["dyld_v1    i386", "dyld_v1  x86_64", "dyld_v1 x86_64h", "dyld_v1     ppc", "dyld_v1   armv6",
              "dyld_v1   armv7", "dyld_v1  armv7f", "dyld_v1  armv7s", "dyld_v1  armv7k", "dyld_v1   arm64",
              "dyld_v1  arm64e", "dyld_v1arm64_32"]
PROT = {1: "r--", 3: "rw-", 5: "r-x", 7: "rwx"}


def magic(arch):
    """dyld_v1, then the architecture right-justified, 15 characters and a NUL."""
    text = "dyld_v1" + arch.rjust(15 - len("dyld_v1"))
    return text.encode("ascii") + b"\x00"


def build():
    mappings = [(0x7FF800000000, 0x26BF4000, 0, 5, 5), (0x7FF840000000, 0x3520000, 0x26BF4000, 3, 1)]
    paths = [b"/usr/lib/libSystem.B.dylib\x00", b"/usr/lib/libc++.1.dylib\x00"]
    mapping_off = 0x200
    images_off = mapping_off + 32 * len(mappings)
    paths_off = images_off + 32 * len(paths)
    header = bytearray(0x200)
    header[0:16] = magic("x86_64h")
    struct.pack_into("<IIII", header, 16, mapping_off, len(mappings), 0, 0)      # imagesOffsetOld/CountOld are 0 in a modern cache
    struct.pack_into("<Q", header, 32, 0)                                       # dyldBaseAddress
    header[0x58:0x68] = bytes.fromhex("f25a411f0e2b394f861b412f1a52f90d")        # uuid
    struct.pack_into("<Q", header, 0x68, 1)                                     # cacheType 1 = production
    body = b""
    for address, size, file_off, maxprot, initprot in mappings:
        body += struct.pack("<QQQII", address, size, file_off, maxprot, initprot)
    p = paths_off
    for i, path in enumerate(paths):
        body += struct.pack("<QQQII", 0x7FF800001000 + 0x10000 * i, 0, 0, p, 0)
        p += len(path)
    body += b"".join(paths)
    # Two subcache entries, as dyld_subcache_entry with a 32-byte extension field.
    body += bytes.fromhex("00" * 16) + struct.pack("<Q", 0x40000000) + b".01".ljust(32, b"\x00")
    body += bytes.fromhex("11" * 16) + struct.pack("<Q", 0x80000000) + b".02".ljust(32, b"\x00")
    return bytes(header) + body, images_off, len(paths), paths_off + sum(map(len, paths))


def section(number, title):
    print(f"{number}. {title}")
    print("-" * 72)


def main():
    section(1, "THE MAGIC IS A 16-BYTE TEXT FIELD")
    for arch in ("i386", "x86_64", "x86_64h", "arm64e", "arm64_32"):
        m = magic(arch)
        known = m[:15].decode() in SIGNATURES
        print(f"   {m.hex(' ')}   {m!r:<22} {'in the table' if known else 'unknown'}")
    print()
    print("   dyld_v1, then the architecture right-justified to fill 15 bytes,")
    print("   then a NUL: i386 gets four spaces and arm64_32 none. Ghidra reads")
    print("   sixteen bytes, decodes them, trims them, and compares the string")
    print("   with twelve it knows -- a text comparison, not a number.")
    print()

    section(2, "THE HEADER, THEN A MAPPING TABLE")
    cache, images_off, nimages, end = build()
    mapping_off, mapping_count, old_off, old_count = struct.unpack_from("<IIII", cache, 16)
    uuid = cache[0x58:0x68]
    print(f"   magic          {cache[:16]!r}")
    print(f"   mappingOffset  {mapping_off}   mappingCount {mapping_count}   imagesOffsetOld {old_off}  imagesCountOld {old_count}")
    print(f"   uuid           {uuid.hex()}")
    print()
    print(f"   {'address':<16} {'size':>10} {'fileOffset':>12}  maxProt initProt")
    for i in range(mapping_count):
        address, size, file_off, maxprot, initprot = struct.unpack_from("<QQQII", cache, mapping_off + 32 * i)
        print(f"   {address:#016x} {size:>10} {file_off:>12}  {PROT[maxprot]:<7} {PROT[initprot]}")
    print()
    print("   Every field is little-endian and every address is 64-bit: this is")
    print("   an image of memory, and the mappings say which file bytes land at")
    print("   which addresses with which permissions. Nothing here is code yet.")
    print()

    section(3, "AN IMAGE IS AN ADDRESS AND A PATH")
    for i in range(nimages):
        address, mod_time, inode, path_off, pad = struct.unpack_from("<QQQII", cache, images_off + 32 * i)
        path = cache[path_off:cache.index(b"\x00", path_off)]
        print(f"   image {i}   address {address:#x}   pathFileOffset {path_off}   -> {path.decode()!r}")
    print()
    print("   The path is a NUL-terminated string INSIDE the cache. On a Mac")
    print("   since macOS 11, /usr/lib/libSystem.B.dylib is not a file on disk")
    print("   at all: the linker names it, dyld finds it here, and the only")
    print("   place the name exists is this table.")
    print()

    section(4, "SUBCACHES ARE NAMED BY AN EXTENSION FIELD")
    at = end
    for i in range(2):
        sub_uuid = cache[at:at + 16]
        (vm_off,) = struct.unpack_from("<Q", cache, at + 16)
        ext = cache[at + 24:at + 56]
        print(f"   subcache {i}   uuid {sub_uuid.hex()[:8]}...   vmOffset {vm_off:#x}   extension {ext[:ext.index(b'\x00')].decode()!r}")
        at += 56
    print()
    print("   A modern cache is one file plus subcaches named by appending the")
    print("   extension -- .01, .02 -- and a .symbols file, each a cache with")
    print("   its own magic; the entries here are how the main file finds them.")


if __name__ == "__main__":
    main()
