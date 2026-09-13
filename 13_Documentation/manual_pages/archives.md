# `tar(5)` and `cpio(5)`: numbers written as octal digits inside a binary format

**Level:** reference · for anyone who has run `xxd` on a tar file, seen `ustar` and a column of ASCII zeros, and wanted to know why

**One line:** A ustar header is a 512-byte record of fixed-width fields in which every number is octal ASCII digits and the name is 100 bytes, and both tars on these machines leave that record the moment a name is non-ASCII or too long: bsdtar writes a pax `path=café.txt` line, GNU tar writes a `././@LongLink` entry, neither wrote `hdrcharset` today even for a Latin-1 byte, and a file dated 1960 comes out of the same three formats as base-256, as a decimal `mtime=` line, and as 1969 with no warning.

**The pages:** [`tar(5)`](raw/macos/tar.5.txt) (macOS, dated December 27, 2016; copyright Tim Kientzle 2003–2009 and Martin Matuska 2016; *written as part of the libarchive and bsdtar project*) · [`cpio(5)`](raw/macos/cpio.5.txt) (macOS, December 23, 2011; copyright Tim Kientzle 2007). Ubuntu has no section-5 page for either format and no `cpio` at all; GNU tar's format description lives in `info tar`. Dumped 2026-09-13 by [`dump.sh`](dump.sh); the machines are in [`raw/PROVENANCE-macos.txt`](raw/PROVENANCE-macos.txt) and [`raw/PROVENANCE-linux.txt`](raw/PROVENANCE-linux.txt).

## What the pages are for

Section 5 is file formats, and these two are the file formats every Unix has carried since the 1970s, described by the author of the library that reads all of their variants. `tar(5)` is not a manual for the `tar` command, which has its own page in section 1; it is a description of the bytes, from the 1979 Seventh Edition header through POSIX ustar, the GNU extensions and the pax interchange format, with the `struct` for each. It is the primary source for a question this library asks repeatedly: when a format has to store a number, a name, or a date, what bytes does it write, and what happens when the value does not fit? A tar header answers with a choice that looks strange until you see the reason: it writes numbers as octal digits in ASCII, so that a header is readable on a tape drive from any machine whatever its byte order, and it fixes every field's width in advance, which is [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) with a 100-byte name field, and [A record has to say what it is, how long it is, and whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) with a magic string and a checksum.

`cpio(5)` is the same story for the older archiver, and its interest here is that its variants differ *only* in how they write integers: 16- and 32-bit binary in PDP-11 order, six- and eleven-digit octal ASCII, or eight-digit hex ASCII. It is a page about number formats wearing an archive format's name.

## The page, with notes

### `tar(5)`: the ustar header

```text title="man 5 tar, macOS 26.6.2, dumped 2026-09-13"
           struct header_posix_ustar {
                   char name[100];
                   char mode[8];
                   char uid[8];
                   char gid[8];
                   char size[12];
                   char mtime[12];
                   char checksum[8];
                   char typeflag[1];
                   char linkname[100];
                   char magic[6];
                   char version[2];
                   ...
                   char prefix[155];
                   char pad[12];
           };
```

Add the widths (the elided fields are `uname`, `gname`, `devmajor` and `devminor`, 80 bytes) and they come to 500, plus 12 of padding: one 512-byte record, which is the unit the page calls a *record* and the tape drive read twenty of at a time. Every field is `char[]`, including the numbers. `size[12]` holds the file's length as *octal number in ASCII*, eleven digits and a terminator, so the largest size a ustar header can state is 8 GiB, and `mtime[12]` holds seconds since 1970 the same way. `magic[6]` is the string `ustar` and a NUL at offset 257, which is the byte [`file(1)`](file.md) looks at to say *POSIX tar archive*, and `version[2]` is the two ASCII digits `00`. The name is `name[100]` plus `prefix[155]`, and the paragraph on those two fields is the one to read twice: a longer path *can be split at any / character with the first portion going into the prefix field*, so a 200-byte path fits if it has a slash in the right place and a 120-byte filename with no slash does not fit at all. The experiment below tries exactly that.

```text title="man 5 tar, macOS 26.6.2, dumped 2026-09-13"
     checksum
             Header checksum, stored as an octal number in ASCII.  To compute
             the checksum, set the checksum field to all spaces, then sum all
             bytes in the header using unsigned arithmetic.  This field should
             be stored as six octal digits followed by a null and a space
             character.
```

The checksum is a sum of bytes, and the paragraph goes on to note that *many early implementations of tar used signed arithmetic for the checksum field*, which is the C `char` problem in a file format: on a machine where `char` is signed, a byte above `0x7F` counts as negative, and a header with a non-ASCII name sums differently. *Modern robust readers compute the checksum both ways.* The field's own format, six digits, NUL, space, is measured below as `013332\0 `, and it is the strangest terminator on the page.

### The numeric extensions, and pax

```text title="man 5 tar, macOS 26.6.2, dumped 2026-09-13"
     Another extension, utilized by GNU tar, star, and other newer tar
     implementations, permits binary numbers in the standard numeric fields.
     This is flagged by setting the high bit of the first byte.  The remainder
     of the field is treated as a signed twos-complement value.  This permits
     95-bit values for the length and time fields and 63-bit values for the
     uid, gid, and device numbers.  In particular, this provides a consistent
     way to handle negative time values.
```

Base-256: when the octal digits run out, or the number is negative and octal has no sign, the writer sets bit 7 of the field's first byte and the rest of the field becomes a binary two's-complement integer, big-endian. The high bit can never be set on an ASCII digit, so a reader can tell the two encodings apart from the first byte, which is a small piece of the same design as UTF-8's lead bytes. The experiment below makes GNU tar write one, for a file dated 1960, and reads it back with `int.from_bytes`: [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) is the question the field's first bit answers.

```text title="man 5 tar, macOS 26.6.2, dumped 2026-09-13"
     hdrcharset
             The character set used by the pax extension values.  By default,
             all textual values in the pax extended attributes are assumed to
             be in UTF-8, including pathnames, user names, and group names.
             In some cases, it is not possible to translate local conventions
             into UTF-8.  If this key is present and the value is the six-
             character ASCII string "BINARY", then all textual values are
             assumed to be in a platform-dependent multi-byte encoding.
```

The pax interchange format is POSIX's 2001 answer to everything the 1988 header could not hold: an extra entry of typeflag `x` in front of a file, whose data is lines of `length key=value`, decimal and UTF-8, overriding the fixed fields. `path=` is where a long or non-ASCII name goes (*encoded in UTF8 and can thus include non-ASCII characters*, and the page adds that *compliant writers should store only portable 7-bit ASCII characters in the standard ustar header*), and `hdrcharset` is the one place in any Unix archive format where the encoding of a filename is *declared*. Its two legal values are UTF-8, the default, and `BINARY`, which means *these are the bytes the filesystem gave me and I make no claim about them*, the same admission Python makes with [surrogateescape](../../04_Python/surrogateescape/README.md) and Rust with [`OsStr`](../../05_Rust/osstr_path_and_wtf8/README.md). The measurement below is that neither tar on these machines wrote it, in any format, for any name, including one that is not UTF-8.

### GNU tar, and the Mac

```text title="man 5 tar, macOS 26.6.2, dumped 2026-09-13"
             L       The data for this entry is a long pathname for the
                     following regular entry.
     ...
     magic   The magic field holds the five characters "ustar" followed by a
             space.  Note that POSIX ustar archives have a trailing null.
     ...
   Mac OS X Tar
     The tar distributed with Apple's Mac OS X stores most regular files as
     two separate files in the tar archive.  The two files have the same name
     except that the first one has "._" prepended to the last path element.
```

GNU tar solved long names before POSIX did, with a fake entry called `././@LongLink` of typeflag `L` whose data is the real name; it is what Ubuntu's `tar` writes by default, and the experiment finds it. Its magic is `ustar` followed by a *space* and a version of *space, NUL*, against POSIX's `ustar\0` and `00`, which is how `file` tells the two apart and why a GNU archive is, strictly, not a ustar archive. The `Mac OS X Tar` section describes the `._` AppleDouble entries that carry extended attributes, and they are real: the first archive made below has four entries for two files, because each file carried a `com.apple.provenance` attribute, and Ubuntu's tar lists the `._` halves as ordinary files, with a warning about a `LIBARCHIVE.xattr` key it does not know.

### `cpio(5)`: three ways to write an integer

```text title="man 5 cpio, macOS 26.6.2, dumped 2026-09-13"
     Since PWB UNIX, like the 6th Edition UNIX it was
     based on, only ran on PDP-11 computers, they are in PDP-endian format,
     which has little-endian shorts, and big-endian longs.  That is, the long
     integer whose hexadecimal representation is 0x12345678 would be stored in
     four successive bytes as 0x34, 0x12, 0x78, 0x56.
     ...
   Portable ASCII Format
     ...  It stores
     the same numeric fields as the old binary format, but represents them as
     6-character or 11-character octal values.

           struct cpio_odc_header {
                   char    c_magic[6];
                   ...
                   char    c_filesize[11];
           };
```

The binary format's `0x34 0x12 0x78 0x56` is the third byte order, the one [The bytes do not say which](../../01_Bits_and_Bytes/which_end_comes_first/README.md) mentions and [`byteorder(3)`](byteorder.md) does not: 16-bit words little-endian, and a 32-bit value as two such words with the high word first. The *odc* format, the one POSIX standardised, exists because of that: every field became octal ASCII, so the header is the same bytes on any machine and *if the files being archived are themselves entirely ASCII, then the resulting archive will be entirely ASCII, except for the NUL byte that terminates the name field*. The `newc` format then did the same in hex with eight-digit fields, and the measurement below shows all three magic numbers: `070707` in octal digits, `070701` in hex digits, and `c7 71`, which is octal 070707 as a little-endian 16-bit binary.

## Terms on the page

| On the page | What it means | Read more |
|---|---|---|
| record, block | A 512-byte unit, and a group of them (20 by default, 10240 bytes) read or written in one tape operation; the page notes the words are not standard | [A record has to say what it is, how long it is, and whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) |
| *octal number in ASCII* | The number 3 stored as the bytes `30 30 30 30 30 30 30 30 30 30 33`: readable by eye, machine-independent, and limited to 8 GiB in eleven digits | [Which base did you mean?](../../01_Bits_and_Bytes/which_base_did_you_mean/README.md) |
| *null-terminated string*, *trailing NUL unless they fill the entire field* | The two rules for text fields: a name shorter than 100 bytes ends in NUL; one that is exactly 100 has no room for it | [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) |
| ustar, `magic`, `version` | *Unix Standard TAR*, the 1988 POSIX format; the six bytes `ustar\0` at offset 257 and `00` after them, which `file` uses to name the archive | [`file(1)` and `magic(5)`](file.md) |
| typeflag `0` `1` `2` `5`, `x`, `g`, `L`, `K` | One byte at offset 156: regular file, hard link, symlink, directory; pax per-file and global headers; GNU long name and long link name | [`file(1)` and `magic(5)`](file.md) |
| `name`, `prefix` | 100 and 155 bytes; a long path may be split at a `/` between them, and only there | [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) |
| base-256, *setting the high bit of the first byte* | A binary two's-complement number in a numeric field, flagged by a bit no ASCII digit has; how a 1960 date or a 9 GB file is written | [Bytes, hex and int](../../04_Python/bytes_hex_and_int/README.md) |
| pax interchange format, `x` entry | POSIX 2001's extension: a fake entry whose data is `length key=value` lines that override the fixed header | [A record has to say what it is, how long it is, and whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) |
| `hdrcharset`, `BINARY`, *ISO-IR 10646 2000 UTF-8* | The declared encoding of pax text values: UTF-8 by default, or *raw bytes, no claim*; the only filename-encoding declaration in any Unix archive | [Bytes that are not text](../../04_Python/surrogateescape/README.md) |
| `././@LongLink`, typeflag `L` | GNU's pre-POSIX long-name mechanism: an entry whose data is the following entry's real name | [`find`, and filenames that are bytes](../../11_Tools/find/README.md) |
| `._`, AppleDouble, `copyfile()` | The Mac's second entry per file, carrying extended attributes and resource forks as a binary blob | [`OsStr`, `Path`, and WTF-8](../../05_Rust/osstr_path_and_wtf8/README.md) |
| PDP-endian, *little-endian shorts, and big-endian longs* | `0x12345678` as `34 12 78 56`: the PDP-11's mixed order, preserved in the binary cpio formats | [The bytes do not say which](../../01_Bits_and_Bytes/which_end_comes_first/README.md) |
| odc, *old character* format, `070707` | The all-octal-ASCII cpio header POSIX adopted; six- and eleven-digit fields | [`strtol(3)`](strtol.md) |

## Try it on your machine

**Where the pages and the tools are.**

```text title="Measured 2026-09-13 — macOS 26.6.2 and ubuntu:24.04. Not machine-checked: which pages and programs exist is a fact about the machine."
                       macOS                                                   ubuntu:24.04
$ man -w 5 tar         .../MacOSX.sdk/usr/share/man/man5/tar.5                 No manual entry for tar in section 5
$ man -w 5 cpio        .../MacOSX.sdk/usr/share/man/man5/cpio.5                No manual entry for cpio in section 5
$ tar --version        bsdtar 3.5.3 - libarchive 3.7.4                         tar (GNU tar) 1.35
$ command -v cpio      /usr/bin/cpio  (bsdcpio 3.5.3 - libarchive 3.7.4)       (not installed)
```

**A ustar header, byte by byte.** `café.txt` (three bytes: `ż` and a newline) archived alone with `tar --format ustar` on the Mac; the fields at the offsets the `struct` gives.

```text title="Measured 2026-09-13 — macOS 26.6.2, bsdtar 3.5.3. Not machine-checked."
$ xxd -l 16 u.tar                      00000000: 6361 66c3 a92e 7478 7400 0000 0000 0000  caf...txt.......
$ xxd -s 124 -l 12 u.tar   (size)      0000007c: 3030 3030 3030 3030 3030 3320            00000000003
$ xxd -s 148 -l 8 u.tar    (checksum)  00000094: 3031 3333 3332 0020                      013332.
$ xxd -s 257 -l 8 u.tar    (magic)     00000101: 7573 7461 7200 3030                      ustar.00
GNU tar 1.35, the same file:
$ xxd -s 124 -l 12 gnu.tar (size)      0000007c: 3030 3030 3030 3030 3030 3300            00000000003.
```

The name is the UTF-8 bytes `63 61 66 c3 a9`, put straight into `name[100]`, which the page's *compliant writers should store only portable 7-bit ASCII characters* advises against and both tars do anyway in ustar format. The size is eleven ASCII `0`s and a `3`, then a space on the Mac and a NUL on Ubuntu, both of which POSIX allows. The checksum is six digits, a NUL and a space, exactly as the page specifies. The magic is `ustar`, NUL, `00`, and the typeflag byte at 156 (not shown) is the ASCII `0` of a regular file.

**A name with an accent, and a name of 120 bytes.** Two files, `café.txt` and a 120-byte `nnn…n.txt` with no slash in it, through each tar's default format, then the formats they had to be forced into. `x` marks a pax header entry, `L` a GNU long-name entry.

```text title="Measured 2026-09-13 — macOS 26.6.2 (bsdtar 3.5.3, COPYFILE_DISABLE unset) and ubuntu:24.04 (GNU tar 1.35). Not machine-checked."
macOS, tar cf (default, restricted pax): 9216 bytes, four files for two
    0: PaxHeader/._café.txt        x    ->  20 path=._café.txt
 1024: ._café.txt                  0    (AppleDouble: com.apple.provenance)
 2048: PaxHeader/café.txt          x    ->  18 path=café.txt
 3072: café.txt                    0
 6144: PaxHeader/nnnn...  (name field cut at 100 bytes)   x   -> 130 path=nnnn...txt  (all 120 bytes)
 7168: nnnn...  (name field: the first 100 bytes)          0
ubuntu:24.04, tar cf (default, gnu): 10240 bytes
    0: café.txt                    0    magic 'ustar  \0'   (name field holds the raw UTF-8)
 1024: ././@LongLink               L    data: the 120-byte name
 2048: nnnn...  (first 100 bytes)  0
ubuntu:24.04, tar --format=posix -cf:
    0: ./PaxHeaders/café.txt       x    ->  18 path=café.txt
 1024: café.txt                    0
 2048: ./PaxHeaders/nnnn...        x    -> 130 path=nnnn...txt

$ tar --format ustar -cf ustar.tar café.txt nnn...n.txt
    macOS:   ": Pathname too long"   exit 0   archive holds café.txt only
    ubuntu:  "tar: nnn...n.txt: file name is too long (cannot be split); not dumped"   exit 2
$ grep -a -c hdrcharset *.tar        0 for every archive written today, on both machines
ubuntu, a name holding the single byte e9:  LC_ALL=C.utf8 tar --format=posix  ->  17 path=caf\xe9.txt   (raw byte, no hdrcharset)
macOS, the same name:                       printf 'x' > "$(printf 'caf\xe9.txt')"  ->  Illegal byte sequence  (the filesystem refuses it)
```

Three writers, three answers to the same two names. bsdtar's default is *restricted pax*: a ustar entry when the name fits and is ASCII, an `x` entry with `path=` otherwise, and it counts `é` as *otherwise*, as the page's *compliant writers* paragraph asks. The `._` entries are the page's `Mac OS X Tar` section happening: the source files carried an extended attribute, so each got an AppleDouble companion, and `COPYFILE_DISABLE=1` in the environment makes them go away. GNU tar's default puts the UTF-8 name in the fixed field unremarked and handles the long one with `././@LongLink`, an entry whose name is a lie and whose data is the truth. And ustar, asked to do the impossible, fails in two voices: an error and exit 2 on Ubuntu, a bare message and exit 0 on the Mac, with the file silently absent from the archive. The last two lines are `hdrcharset`: no archive got one, GNU tar wrote the non-UTF-8 byte into `path=` as it was, and on the Mac the question could not even be asked, because APFS refused to create the name: [`find`, and filenames that are bytes](../../11_Tools/find/README.md).

**A file dated 1960.** Negative seconds since the epoch, which eleven octal digits cannot express, through three formats on each machine.

```text title="Measured 2026-09-13 — macOS 26.6.2 (bsdtar 3.5.3, COPYFILE_DISABLE=1) and ubuntu:24.04 (GNU tar 1.35); touch -t 196001010000 on the Mac, touch -d '1960-01-01 00:00:00 UTC' on Ubuntu. Not machine-checked."
                  mtime field (offset 136, 12 bytes)                 pax line               tar tvf shows      stderr, exit
macOS   pax       ff ff ff ff ff ff ff ed 30 4e d0 20 (base-256)     20 mtime=-315601200    Jan 1 1960         exit 0
macOS   ustar     (entry not written; archive is empty)              -                      -                  ": File modification time too large", exit 0
macOS   gnutar    30 30 30 30 30 30 30 30 30 30 30 00 (all zeros)    -                      Dec 31 1969        exit 0, no message
ubuntu  gnu       ff ff ff ff ff ff ff ff ed 30 08 80 (base-256)     -                      1960-01-01         exit 0
ubuntu  posix     30 30 30 30 30 30 30 30 30 30 30 00 (all zeros)    20 mtime=-315619200    1960-01-01         exit 0
ubuntu  ustar     (entry not written)                                -                      -                  "value -315619200 out of time_t range 0..8589934591", exit 2

$ python3 -c "b=bytes.fromhex('ffffffffffffffffed300880'); v=int.from_bytes(bytes([b[0]&0x7f])+b[1:],'big')-(1<<95); print(v)"
-315619200
```

Six outcomes for one date. The two base-256 rows are the page's numeric extension: first byte `ff`, high bit set, the rest two's complement, and Python reads it back as −315,619,200 (the Mac's differs by 18,000 because `touch -t` is local time). The two `all zeros` rows are the fixed field giving up; in pax format the truth is in the `mtime=` line and the listing is right, and in bsdtar's `gnutar` format there is no such line, nothing is said, and the file has become New Year's Eve 1969. The two ustar rows are the format refusing, once loudly and once at exit 0. Which of the six you get is a fact about the writer and the flag, not about the file: [Packing a record](../../07_Real_Data/packing_a_record/README.md).

**A cpio header in odc.** The Mac's `cpio -o -H odc`, with the fields cut at the widths the `struct` gives.

```text title="Measured 2026-09-13 — macOS 26.6.2, bsdcpio 3.5.3. Not machine-checked."
$ printf 'café.txt\n' | cpio -o -H odc | xxd | head -6
00000000: 3037 3037 3037 3737 3737 3737 3030 3030  0707077777770000
00000010: 3031 3130 3036 3434 3030 3037 3635 3030  0110064400076500
00000020: 3030 3030 3030 3030 3031 3030 3030 3030  0000000001000000
00000030: 3135 3235 3135 3232 3233 3030 3030 3031  1525152223000001
00000040: 3230 3030 3030 3030 3030 3033 6361 66c3  200000000003caf.
00000050: a92e 7478 7400 c5bc 0a30 3730 3730 3730  ..txt....0707070
magic '070707'  dev '777777'  ino '000001'  mode '100644' = 33188  uid '000765' = 501  gid '000000'
nlink '000001'  rdev '000000'  mtime '15251522230' = 1789306008  namesize '000012' = 10  filesize '00000000003' = 3
name b'caf\xc3\xa9.txt\x00'  then the data c5 bc 0a  then the next header's 070707
$ printf 'café.txt\n' | cpio -o -H newc | xxd -l 16      00000000: 3037 3037 3031 3065 6263 3237 3163 3030  0707010ebc271c00
$ printf 'café.txt\n' | cpio -o -H bin  | xxd -l 16      00000000: c771 0700 0100 a481 f501 0000 0100 0000  .q..............
```

Every field is digits; the first 76 bytes of the archive are printable. `mode` is `100644`, octal, the same number `ls -l` renders as `-rw-r--r--`; `namesize` is `000012` octal, ten, because it counts the NUL after the name; and there is no padding, so the file data follows the name immediately and the next header starts the byte after the data. `newc` begins `070701` and continues in hex. `bin` begins `c7 71`, which read as a little-endian 16-bit word is `0x71c7`, octal 070707: the same magic number in the third notation. Parsing any of these is [`strtol(3)`](strtol.md) with the base named explicitly.

**Each machine reads the other's archive, and how the name comes back.**

```text title="Measured 2026-09-13 — macOS 26.6.2 (bsdtar 3.5.3) and ubuntu:24.04 (GNU tar 1.35), archives exchanged through a shared directory. Not machine-checked."
ubuntu, tar tvf of the Mac's default archive (first three lines):
-rw-r--r-- amasa/wheel     163 2026-09-13 13:26 ._café.txt
tar: Ignoring unknown extended header keyword 'LIBARCHIVE.xattr.com.apple.provenance'
-rw-r--r-- amasa/wheel       3 2026-09-13 13:26 café.txt
macOS reads Ubuntu's two archives, names as bytes (LC_ALL=en_US.UTF-8 tar tf ... | xxd -p):
    from the gnu-format archive     636166c3a92e7478740a     cafe + c3 a9   (the bytes in the header)
    from the posix-format archive   63616665cc812e7478740a   cafe + 65 cc 81  (e, then U+0301, the decomposed form)
    the name field in both archives 636166c3a9...            identical
```

Ubuntu's tar reads the Mac's pax archive as the page predicts: the `._` entries are *regular files, where the metadata can be examined as necessary*, and the vendor key is ignored with a note. The Mac's reading of Ubuntu's archives is the finding. The same nine bytes are in both name fields, and bsdtar lists them two different ways: from the GNU-format archive as they are, and from the pax archive with `é` replaced by `e` and a combining acute, the decomposed form. The difference is the format's declaration. A pax `path=` is UTF-8 by definition, so libarchive treats it as text and, on macOS, normalises it for the filesystem; a GNU header field is bytes with no declared encoding, so it passes through. Nothing on the page says so, and a `diff` of two extracted directory listings would find a name that is not equal to itself: [`OsStr`, `Path`, and WTF-8](../../05_Rust/osstr_path_and_wtf8/README.md).

## Where the page is dated, and what it does not say

**`tar(5)` is dated December 27, 2016** and describes a 1979 format, a 1988 one and a 2001 one, all still written today; its dates are the formats', not the page's. It carries two `XXX` markers of its own and a `Solaris Tar` section that is mostly one. Its *Mac OS X Tar* section is fifteen years old in name and current in fact, as the `._` entries above show.

**`hdrcharset=BINARY` is on the page and not in either implementation's output.** GNU tar 1.35 wrote a non-UTF-8 byte into `path=` with no declaration; bsdtar never got the chance, because the filesystem it runs on will not hold such a name. The page's *platform-dependent multi-byte encoding* escape hatch is real and, on these two machines today, unused. Nor does the page say what a reader does with a `path=` it cannot represent, or that a reader on macOS will normalise one: the decomposition above is documented nowhere in section 5.

**Neither page says what happens when a value does not fit.** The six-outcome table for a 1960 date is measured, not documented: the page describes base-256 as an extension GNU tar *supports*, and does not say that the same libarchive writes it in one format and zeros in another.

**`cpio(5)` ends with questions.** *XXX when did "newc" appear? Who invented it?* A format the Linux kernel's initramfs is written in, and its own page does not know its birthday. The `HP variants` section is two `XXX`s and a verb.

## See also

- [`byteorder(3)`, `swab(3)` and `bitstring(3)`](byteorder.md) — the two byte orders `cpio(5)` mixes in one integer, and the functions for them
- [`file(1)` and `magic(5)`](file.md) — `ustar` at offset 257, and the one byte at 261 that says *(GNU)*
- [`strtol(3)`](strtol.md) — parsing `00000000003` and `070707` with the base stated
- [Fixed-width byte fields](../../07_Real_Data/fixed_width_byte_fields/README.md) — a 100-byte name field holds 100 ASCII letters or 50 Polish ones
- [A record has to say what it is, how long it is, and whether it arrived](../../08_Build_Your_Own/framing_a_format/README.md) — magic, length and checksum, which the ustar header has all three of
- [Packing a record](../../07_Real_Data/packing_a_record/README.md) — the layout written down somewhere; here, on a man page with a `struct`
- [Bytes that are not text](../../04_Python/surrogateescape/README.md) — what `hdrcharset=BINARY` means in Python
- [What the page does not say](../what_the_page_does_not_say/README.md) — the general rule, and a page that marks its own gaps with `XXX`
