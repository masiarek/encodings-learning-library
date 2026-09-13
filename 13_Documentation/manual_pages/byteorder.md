# `byteorder(3)`, `swab(3)` and `bitstring(3)`: which end comes first, in C

**Level:** reference · for anyone who has typed `man htonl` and wanted to know what it does on the machine in front of them

**One line:** `htonl` and `htons` reverse the bytes of a number on both of these x86_64 machines and would do nothing on a big-endian one, which is all the 1993 page's *null macros* sentence means; `swab(3)` swaps adjacent byte pairs, which is exactly UTF-16LE to UTF-16BE with the byte order mark turning from `ff fe` into `fe ff`; and `bitstring(3)` is a set of macros for naming one bit inside a byte, on the Mac only, with bit 0 the least significant.

**The pages:** [`byteorder(3)`](raw/macos/byteorder.3.txt) (macOS, dated June 4, 1993; copyright 1983, 1991, 1993) · [`swab(3)`](raw/macos/swab.3.txt) (macOS, February 24, 2010; copyright 1990, 1991, 1993) · [`bitstring(3)`](raw/macos/bitstring.3.txt) (BSD 4, July 19, 1993; copyright 1989, 1991, 1993). Ubuntu has `byteorder(3)` and `swab(3)` in section 3 and no `bitstring(3)`, no `<bitstring.h>`, and no `htonll`. Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

These are section-3 pages, library functions, and they are in an encodings library because byte order is the first encoding decision a program makes about anything wider than a byte. A 32-bit number has four bytes and a file or a wire has to carry them in *some* order; [The bytes do not say which](../../01_Bits_and_Bytes/which_end_comes_first/README.md) is the lesson, and these three pages are the C library's tools for it. `byteorder(3)` converts between the order the CPU uses and the order the Internet protocols fixed at the start of the 1980s, which is big-endian; it was written for `gethostbyname`, and it is the page every socket tutorial sends you to. `swab(3)` is older and simpler, from Seventh Edition Unix: a copy that swaps every pair of bytes, now mostly useful for one thing, UTF-16. `bitstring(3)` addresses the order *inside* a byte: a set of macros for treating an array of bytes as an array of bits, which is the layer below [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md).

All three are BSD pages that macOS ships unchanged from 1993 apart from the two 64-bit functions Apple added in 2014. Ubuntu documents the first two from the Linux man-pages project under the same names and has never had the third, because `<bitstring.h>` is a BSD header that glibc does not carry.

## The page, with notes

### `byteorder(3)`: network order and host order

```text title="man 3 byteorder, macOS 26.6.2, dumped 2026-09-13"
     These routines convert 16 bit, 32 bit, and 64 bit quantities between
     network byte order and host byte order.  (Network byte order is big
     endian, or most significant byte first.)  On machines which have a byte
     order which is the same as the network order, routines are defined as
     null macros.
```

Two names for two orders, and only one of them is fixed. *Network byte order* is big-endian by definition: the most significant byte goes first, so `0x0A0B0C0D` is sent as `0a 0b 0c 0d`, the order you would write it in. *Host byte order* is whatever the CPU does, and the page does not say what that is on the machine it ships on, because the same page ships on every machine. This Mac is x86_64 and so is the Ubuntu container, and both are little-endian: `sysctl hw.byteorder` says `1234`, `lscpu` says *Little Endian*, and the experiment below shows `0x0A0B0C0D` sitting in memory as `0d 0c 0b 0a`. So on both machines the four functions are byte reversals. On a big-endian host they would be *null macros*, `#define htonl(x) (x)`, and code that calls them would compile to nothing, which is the whole design: you write `htonl` everywhere and let the header decide whether it does anything. The names themselves are 1983: the *l* in `htonl` is a C `long`, which was 32 bits on the VAX, and the `SYNOPSIS` has quietly changed the type to `uint32_t` while keeping the letter.

```text title="man 3 byteorder, macOS 26.6.2, dumped 2026-09-13"
HISTORY
     The functions htonl, htons, ntohl, ntohs appeared in 4.2BSD.

     The functions htonll and ntohll first appeared in OS X 10.10 (Yosemite).

BUGS
     On the VAX bytes are handled backwards from most everyone else in the
     world.  This is not expected to be fixed in the near future.
```

The `HISTORY` section is where the page admits to a date: the 64-bit pair is Apple's, from 2014, and Ubuntu's glibc has no `htonll` (the experiment below gets an *undefined reference*; glibc's own spelling is `htobe64`, from the `<endian.h>` family documented in `endian(3)` there and absent from the Mac's manual). The `BUGS` entry is a 1983 joke about a computer line that has been out of production for decades. The VAX was little-endian, like this Mac, and the joke's premise, that big-endian was normal, was true of the machines the Internet was designed on and stopped being true of desktops when the PC won.

### `swab(3)`: swap adjacent bytes

```text title="man 3 swab, macOS 26.6.2, dumped 2026-09-13"
     The function swab() copies nbytes bytes from the location referenced by
     src to the location referenced by dest, swapping adjacent bytes.

     The argument nbytes should be an even number.  If nbytes is odd, swab()
     copies and exchanges nbytes -1 bytes and the disposition of the last byte
     is unspecified.
```

Pairs, not values: `swab` does not know or care that its input is 16-bit numbers, it swaps bytes 0 and 1, 2 and 3, and so on. That is precisely the difference between UTF-16LE and UTF-16BE, which store every code unit as the same two bytes in opposite order, so `swab` over a UTF-16LE buffer produces the UTF-16BE encoding of the same text and turns the byte order mark `ff fe` into `fe ff` on the way: [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md). It is the operation [Swap Bytes](../../15_Hex/swap_bytes/README.md) performs on a 16-bit selection in a hex editor, and `dd conv=swab` at the shell: [`dd(1)`](dd.md). The *odd nbytes* sentence is the one to remember: a UTF-16 buffer with an odd length has a broken code unit at the end, and `swab` will not tell you.

### `bitstring(3)`: one bit at a time

```text title="man 3 bitstring, macOS 26.6.2, dumped 2026-09-13"
     The macros bit_clear() and bit_set() clear or set the zero-based numbered
     bit bit, in the bit string name.
     ...
     The bit_test() macro evaluates to non-zero if the zero-based numbered bit
     bit of bit string name is set, and zero otherwise.
     ...
     The macros bit_clear(), bit_set() and bit_test() will evaluate the bit
     argument more than once, so avoid using pre- or post-, increment or
     decrement.
```

A `bitstr_t` is an `unsigned char`, one byte, and a bit string is an array of them addressed by bit number: bit 0 to bit 7 are in byte 0, bit 8 to bit 15 in byte 1. What the page never says is which bit of the byte is bit 0, and the experiment below answers it: setting bit 0 writes `01`, so bit 0 is the least significant bit, the one worth 1, and bit 7 is the one worth 128, the *high order bit* [`utf8(5)`](utf8.md) says is set on every byte of a multibyte character. `bit_test` returns *non-zero*, and the measurement shows it returning 32 for bit 5, the masked byte, not a 1. And the last paragraph is a warning about macros that any C programmer of 1989 needed and any C programmer today still does: `bit_set(name, i++)` increments twice.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| network byte order | Big-endian, fixed by the Internet protocols; the order `0x0A0B0C0D` is written on the wire, `0a 0b 0c 0d` | [The bytes do not say which](../../01_Bits_and_Bytes/which_end_comes_first/README.md) |
| host byte order | Whatever the CPU does; little-endian on both machines here, `0d 0c 0b 0a` in memory | [The bytes do not say which](../../01_Bits_and_Bytes/which_end_comes_first/README.md) |
| big endian, *most significant byte first* | The byte worth the most comes first; matches the way numbers are written | [The bytes do not say which](../../01_Bits_and_Bytes/which_end_comes_first/README.md) |
| *null macros* | On a big-endian host `htonl(x)` is defined as `(x)`; the call costs nothing and changes nothing | [Packing a record](../../07_Real_Data/packing_a_record/README.md) |
| `htonl`, `htons`, `ntohl`, `ntohs` | Host-to-network long and short, and back; *long* here means 32 bits and *short* 16, the 1983 sizes | [Packing a record](../../07_Real_Data/packing_a_record/README.md) |
| `uint16_t`, `uint32_t`, `uint64_t` | Exact-width unsigned integers from `<stdint.h>`, which is what the words *short* and *long* in the function names have been replaced by | [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| `htonll`, `ntohll` | The 64-bit pair, Apple's since OS X 10.10; not in POSIX and not in glibc, whose spelling is `htobe64` | |
| `<arpa/inet.h>` | The header, named for the ARPA Internet: these functions were written for IP addresses and port numbers | |
| 4.2BSD, VAX | The 1983 Unix release the four functions arrived in, and the little-endian machine it ran on | [From the telegraph to Unicode](../../09_History/from_telegraph_to_unicode/README.md) |
| *POSIX.1-200x* | The `STANDARDS` line's name for a draft of POSIX.1-2001; the *x* was never filled in | [A page has a date](../a_page_has_a_date/README.md) |
| *swapping adjacent bytes* | Bytes 0↔1, 2↔3, …; a pairwise operation that knows nothing about values | [Swap Bytes](../../15_Hex/swap_bytes/README.md) |
| `restrict`, *objects that overlap* | The C99 promise that `src` and `dest` are separate memory; `swab` on overlapping buffers is undefined | |
| `ssize_t nbytes`, *if nbytes is negative* | A signed size, so a negative count is possible and the page says it does nothing | |
| bit string, `bitstr_t` | An array of `unsigned char` addressed by bit number; `bitstr_size(n)` bytes hold `n` bits | [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) |
| *zero-based numbered bit* | Bit 0 is the first, and (measured, not stated) the least significant bit of byte 0 | [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) |
| `bit_ffs`, `bit_ffc` | Find first set, find first clear: the index of the first 1 or 0 bit, or −1 | |
| `bit_decl`, `bit_alloc` | Declare a bit string on the stack, or allocate one with `malloc` | |
| *evaluate the bit argument more than once* | The classic macro hazard: `bit_set(s, i++)` increments `i` twice | |

## Try it on your machine

**What each machine says its order is.** Three independent witnesses, all agreeing.

```text title="Measured 2026-09-13 — macOS 26.6.2 (x86_64) and ubuntu:24.04 (x86_64). Not machine-checked: byte order is a fact about the CPU."
                                                  macOS                     ubuntu:24.04
$ uname -m                                        x86_64                    x86_64
$ sysctl hw.byteorder / lscpu | grep 'Byte Order' hw.byteorder: 1234        Byte Order: Little Endian
$ python3 -c "import sys; print(sys.byteorder)"   little                    little
```

**The page's functions, watched in memory.** A C program that calls `htonl`, `htons` and `swab`, then prints each result's bytes in the order they sit in memory. Identical output on both machines, compiled with Apple clang 21 and gcc 13.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang 21.0.0) and ubuntu:24.04 (gcc 13.3.0): byte-identical output. Not machine-checked."
htonl(0x0A0B0C0D) = 0x0D0C0B0A    htons(0xFEFF) = 0xFFFE
host 0x0A0B0C0D in memory:    0d 0c 0b 0a
htonl() result in memory:     0a 0b 0c 0d
host 0xFEFF in memory:        ff fe
htons() result in memory:     fe ff
ntohl(htonl(x)) == x: yes
UTF-16LE "cafe" with BOM:     ff fe 63 00 61 00 66 00 e9 00
after swab():                 fe ff 00 63 00 61 00 66 00 e9
```

Line one is the surprise for anyone who expected `htonl` to be an identity: the *value* it returns is `0x0D0C0B0A`, a different number, because on a little-endian host the only way to get the bytes `0a 0b 0c 0d` into memory is to store the number whose little-endian spelling that is. Lines two and three are the same fact from the memory side. The `htons` lines are the byte order mark: `U+FEFF` stored natively on this machine is `ff fe`, which is why a UTF-16 file written by a program that just dumps its `wchar_t` array begins with those two bytes. The last two lines are `swab` over `café` in UTF-16LE: every pair reversed, BOM included, and the result is the UTF-16BE encoding of the same four characters: [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md).

**The same conversion at the shell, and where the two `iconv`s disagree.**

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple iconv) and ubuntu:24.04 (GNU iconv, glibc 2.39). Not machine-checked."
                                                                        macOS                    ubuntu:24.04
$ printf 'caf\xc3\xa9' | iconv -f UTF-8 -t UTF-16LE | xxd -p            630061006600e900         630061006600e900
$ printf 'caf\xc3\xa9' | iconv -f UTF-8 -t UTF-16LE | dd conv=swab | xxd -p   00630061006600e9   00630061006600e9
$ printf 'caf\xc3\xa9' | iconv -f UTF-8 -t UTF-16BE | xxd -p            00630061006600e9         00630061006600e9
$ printf 'caf\xc3\xa9' | iconv -f UTF-8 -t UTF-16 | xxd -p              feff00630061006600e9     fffe630061006600e900
```

`dd conv=swab` is `swab(3)` as a filter, and its output is byte-identical to asking for `UTF-16BE` directly. The last row is the finding: ask for plain `UTF-16`, the form that is supposed to carry a byte order mark so the reader can tell, and Apple's `iconv` writes big-endian with `fe ff` while GNU's writes little-endian with `ff fe`. Both are valid UTF-16, both begin with the mark that says which, and the difference is why [An encoding is four layers](../../03_Encodings/the_encoding_model/README.md) insists that `UTF-16` and `UTF-16LE` are different names.

**The bit string, and what Ubuntu is missing.** The Mac program sets bits 0, 5, 9 and 15 of a 16-bit string and prints the two bytes; the same source on Ubuntu does not compile, and neither does a call to `htonll`, while `swab` needs a feature macro that the Mac does not.

```text title="Measured 2026-09-13 — macOS 26.6.2 (Apple clang 21.0.0) and ubuntu:24.04 (gcc 13.3.0, glibc 2.39). Not machine-checked."
macOS:
sizeof(bitstr_t) = 1, bitstr_size(16) = 2
bits 0,5,9,15 set -> bytes: 21 82
bit_ffs = 0
bit_ffc = 1
bit_test(5) = 32, bit_test(6) = 0
after bit_nclear(0,7): 00 82
htonll(0x0102030405060708) prints 807060504030201

ubuntu:24.04:
bits.c:2:10: fatal error: bitstring.h: No such file or directory
hll.c:(.text+0x1b): undefined reference to `htonll'
bo2.c:24:5: warning: implicit declaration of function ‘swab’ [-Wimplicit-function-declaration]   (without #define _XOPEN_SOURCE 700)
$ man -w 3 bitstring                No manual entry for bitstring in section 3
$ man -w 3 htobe32                  /usr/share/man/man3/endian.3.gz      (macOS: No manual entry for htobe32)
```

`21 82`: bit 0 is the `1` in `0x21` and bit 5 is the `0x20`, so bit 0 is the least significant bit of byte 0; bit 9 is the `0x02` of byte 1 and bit 15 its `0x80`. That is the numbering [Hex is a shorthand](../../01_Bits_and_Bytes/hex_is_a_shorthand/README.md) uses when it calls `0x80` bit 7, and it is the opposite of the way the bytes themselves are numbered in the string, which is a small endianness of its own. The Ubuntu half shows three things the page cannot tell you: the header does not exist there, the 64-bit functions do not exist there, and glibc hides `swab`'s prototype unless the program asks for the X/Open interfaces.

**The same question in Python.** `int.from_bytes` takes the order as an argument, which is the honest interface: the bytes do not say.

```text title="Measured 2026-09-13 — python3 3.14 on macOS 26.6.2 and 3.12 on ubuntu:24.04: identical. Not machine-checked."
$ python3 -c "b=bytes.fromhex('0a0b0c0d'); print(hex(int.from_bytes(b,'big')), hex(int.from_bytes(b,'little')))"
0xa0b0c0d 0xd0c0b0a
$ python3 -c "import struct; print(struct.pack('<I',0x0A0B0C0D).hex(), struct.pack('>I',0x0A0B0C0D).hex(), struct.pack('!I',0x0A0B0C0D).hex(), struct.pack('=I',0x0A0B0C0D).hex())"
0d0c0b0a 0a0b0c0d 0a0b0c0d 0d0c0b0a
```

`struct`'s `!` is *network*, and it is the same as `>` because network order is big-endian by definition; `=` is *native*, and on these machines it is the same as `<`. That is `byteorder(3)` in four characters: [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md).

## Where the page is dated, and what it does not say

**`byteorder(3)` is dated June 4, 1993**, its `STANDARDS` line cites a draft (*POSIX.1-200x*) that became POSIX.1-2001, and its `BUGS` section is about a computer that stopped being made in 2000. The two 2014 functions are the only sign the page has been touched. It never says which order *this* host has, so a reader has to measure it, as above.

**It does not mention the modern spellings.** glibc's `htobe32`, `htole32` and their `<endian.h>` family, the Mac's `OSSwapInt32` in `<libkern/OSByteOrder.h>`, and the `__builtin_bswap32` both compilers provide all reverse `0x0A0B0C0D` to `0x0D0C0B0A` on these machines, and none is on the page. Nor is the trick of reading a number with `memcpy` and shifts, which needs no swapping function at all: [Packing a record](../../07_Real_Data/packing_a_record/README.md).

**`swab(3)` does not mention UTF-16**, the one reason most people reach for it today, or `dd conv=swab`, the same operation as a command.

**`bitstring(3)` does not say which bit is bit 0.** The measurement above does. It is also a page for a header that exists on one of the two machines and a manual entry that exists on one, and neither machine's page says so.

## See also

- [`dd(1)`](dd.md) — `conv=swab`, the same pairwise swap as a filter
- [`utf8(5)` and `utf-8(7)`](utf8.md) — where *high order bit* means bit 7, the one `bitstring(3)` numbers last
- [`stdio(3)` and the byte streams](stdio.md) — the functions that write these bytes to a file, in whatever order you hand them
- [The bytes do not say which](../../01_Bits_and_Bytes/which_end_comes_first/README.md) — the lesson these three pages are the C API for
- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md) — `ff fe` and `fe ff`, and why UTF-8 has no order to resolve
- [UTF-16 and surrogates](../../03_Encodings/utf16_and_surrogates/README.md) — the encoding `swab` converts between the two forms of
- [Packing a record](../../07_Real_Data/packing_a_record/README.md) — the layout has to be written down somewhere; `htonl` is one place
- [Swap Bytes](../../15_Hex/swap_bytes/README.md) — the same operation in a hex editor's dialog
- [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) — `int.from_bytes(b, 'big')`, the interface that makes you say
- [A byte is eight bits](../../01_Bits_and_Bytes/a_byte_is_eight_bits/README.md) — the unit `bitstring(3)` cuts into eight
