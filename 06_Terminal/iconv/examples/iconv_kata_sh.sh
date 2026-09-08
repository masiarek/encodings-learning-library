#!/usr/bin/env bash
# Kata solution: four iconv commands over one six-byte file.
# Every line below is byte-identical on macOS and Ubuntu — the -c row on
# purpose, because four bytes follow the invalid one and the platforms only
# disagree when exactly ONE does.
#
# Run:  bash iconv_kata_sh.sh
set -u
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
hx() { od -An -tx1 | tr -d '\n' | tr -s ' ' | sed 's/^ *//; s/ *$//'; }

printf 'a\351b\303\251\n' > f          # 61 e9 62 c3 a9 0a

run() {
  eval "$1" > o.bin 2>/dev/null; st=$?
  printf '   %-38s exit=%s  out=%s\n' "$1" "$st" "$(hx < o.bin)"
}

echo "THE FILE"
echo "   f = $(hx < f)"
echo "   'a', then the LATIN-1 byte for e-acute, then 'b', then e-acute"
echo "   written properly in UTF-8, then a newline. One file, two spellings"
echo "   of the same letter — which is what makes it worth four commands."
echo
echo "THE FOUR COMMANDS"
run "iconv -f UTF-8      -t UTF-8 f"
run "iconv -f ISO-8859-1 -t UTF-8 f"
run "iconv -c -f UTF-8   -t UTF-8 f"
run "iconv -f UTF-8      -t ASCII//IGNORE f"
echo
echo "WHAT EACH ONE DID"
echo "   1  The validator. e9 is not a legal UTF-8 start byte, so iconv stops"
echo "      there and exits 1 — after writing the 61 it had already converted."
echo "      A refusal is not an empty file; partial output is normal."
echo "   2  No failure is possible: Latin-1 has all 256 bytes. e9 became the"
echo "      correct c3 a9, and the ALREADY-correct c3 a9 became c3 83 c2 a9."
echo "      Half the file was repaired and half was broken, in one pass,"
echo "      exit 0. This is what a wrong -f looks like from the outside."
echo "   3  -c skips the byte it cannot read and keeps going: e9 is gone and"
echo "      everything else survives, exit 0."
echo "   4  //IGNORE drops what ASCII cannot hold — the invalid byte AND the"
echo "      valid e-acute, because neither is an ASCII character — and still"
echo "      exits 1."
echo
echo "WHICH ANSWERS TRAVEL, AND THE BYTE TO WATCH"
echo "   Rows 1, 2 and 4 are identical on macOS and Ubuntu. Row 3 is identical"
echo "   HERE and is the fragile one: after -c skips e9 there are four bytes"
echo "   left, and macOS only differs when exactly one byte follows the skip,"
echo "   in which case it discards it. Delete 'b' and the e-acute from f and"
echo "   the two platforms print different answers for row 3."
echo "   The byte to watch is e9. It is a perfectly good e-acute in one table"
echo "   and not a character at all in the other, and every line above is a"
echo "   different policy for that one disagreement."
