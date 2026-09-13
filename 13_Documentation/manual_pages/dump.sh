#!/bin/bash
# Dump the macOS man pages this folder annotates, verbatim, into raw/macos/.
#
#   bash 13_Documentation/manual_pages/dump.sh          # from the repo root
#
# Each page is rendered exactly as `man SECTION NAME` prints it into a pipe --
# 78 columns, mandoc's own layout -- and then passed through `col -bx`, which
# removes the backspace-overstrike bold/underline and turns tabs into spaces.
# Nothing else is done to the text: a fresh dump should diff empty against
# the committed one on the same machine, which is the point of keeping the
# script beside the files. The machine it ran on is written to
# raw/PROVENANCE.txt, because a man page is documentation OF a machine.
#
# The list is grouped the way the annotated pages group them. A name that
# `man` resolves to a different file (base64 -> bintrans.1) is dumped under
# the name you would type.
set -u
cd "$(dirname "$0")" || exit 1
# The locale decides the bytes: under a UTF-8 LC_CTYPE mandoc writes real
# dashes and its special-character escapes as glyphs, under C it writes ASCII
# (EUR for the euro escape, 'e for an e-acute). Pin it, so the dump is the
# ASCII rendering whatever terminal the script is run from -- and so `col`,
# which under the C locale on this Mac deletes any byte above 0x7f, never
# meets one.
export LC_ALL=C
out=raw/macos
mkdir -p "$out"
n=0; missing=0
while read -r sec name; do
  case "$sec" in ''|'#'*) continue ;; esac
  if ! path=$(man -w "$sec" "$name" 2>/dev/null); then
    echo "MISSING  $name($sec)" >&2; missing=$((missing+1)); continue
  fi
  man "$sec" "$name" 2>/dev/null | col -bx > "$out/$name.$sec.txt"
  n=$((n+1))
done <<'LIST'
# --- the encodings themselves (section 5 = file formats)
5 utf8
5 utf2
5 euc
5 big5
5 gb2312
5 gbk
5 gb18030
5 mskanji
# --- the tables
7 ascii
7 environ
# --- the C multibyte API
3 multibyte
3 mbrtowc
3 wcrtomb
3 mbsrtowcs
3 wcsrtombs
3 mbstowcs
3 wcstombs
3 mblen
3 mbrlen
3 mbtowc
3 wctomb
3 btowc
3 wctob
3 mbsinit
3 mbrune
3 rune
# --- character classes and case
3 ctype
3 isalpha
3 isprint
3 isascii
3 toascii
3 tolower
3 toupper
3 wctype
3 iswalpha
3 iswctype
3 towlower
3 towupper
3 wctrans
3 towctrans
3 wcwidth
3 wcswidth
# --- locale
1 locale
3 setlocale
3 localeconv
3 nl_langinfo
3 xlocale
3 newlocale
3 uselocale
3 duplocale
3 querylocale
# --- collation
3 strcoll
3 strxfrm
3 wcscoll
3 wcsxfrm
3 strcasecmp
3 wcscasecmp
# --- iconv
1 iconv
3 iconv
3 iconvctl
3 iconvlist
# --- vis: escaping into ASCII, as a C API and a command
1 vis
1 unvis
3 vis
3 unvis
# --- bytes and their order
3 byteorder
3 swab
3 bitstring
# --- streams: text mode, binary mode, wide orientation
3 stdio
3 fopen
3 fgets
3 fgetln
3 getline
3 fgetws
3 getwc
3 putwc
3 fwide
3 printf
3 wprintf
1 printf
1 echo
3 strtol
3 strtoul
# --- patterns
7 re_format
3 regex
3 fnmatch
3 glob
1 grep
1 sed
# --- dump tools
1 hexdump
1 od
1 xxd
1 strings
1 file
5 magic
# --- binary to text
1 base64
1 uuencode
1 uudecode
# --- text tools: columns and characters
1 tr
1 cut
1 fold
1 fmt
1 expand
1 unexpand
1 col
1 colrm
1 pr
1 ul
1 rev
1 wc
# --- text tools: lines and fields
1 cat
1 head
1 tail
1 nl
1 split
1 csplit
1 tee
1 look
1 uniq
1 sort
1 comm
1 join
1 paste
1 lam
1 rs
1 jot
1 seq
1 xargs
# --- comparing and summing
1 diff
1 cmp
1 cksum
1 md5
# --- dd
1 dd
# --- the terminal
4 tty
1 stty
# --- the manual itself
1 man
1 mandoc
7 mandoc_char
# --- archives
5 tar
5 cpio
LIST
{
  echo "macOS dump: $(date '+%Y-%m-%d')"
  echo "  $(sw_vers -productName) $(sw_vers -productVersion) ($(uname -m)), Darwin $(uname -r)"
  echo "  man: $(man -w 5 utf8)"
  echo "  rendered with: LC_ALL=C man SECTION NAME | col -bx   (mandoc, 78 columns, ASCII rendering)"
  echo "  pages: $n dumped, $missing missing"
} > raw/PROVENANCE-macos.txt
cat raw/PROVENANCE-macos.txt
