#!/usr/bin/env bash
# Answer key: a filename is bytes, and -name compares them.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
mkdir d; cd d
printf '' > "$(printf 'caf\303\251.txt')"        # composed é: c3 a9

echo "ONE FILE, WHOSE NAME IS BYTES"
name=$(ls)
printf '   ls says      %s\n' "$name"
printf '   name bytes   %s\n' "$(printf '%s' "$name" | xxd -p)"
echo
echo "SEARCH FOR IT TWO WAYS"
comp=$(printf 'caf\303\251.txt')                  # NFC: c3 a9
decomp=$(printf 'cafe\314\201.txt')               # NFD: 65 cc 81
printf '   find . -name "<NFC>"    %s\n'   "$(find . -name "$comp"   | wc -l | tr -d ' ') hit(s)"
printf '   find . -name "<NFD>"    %s\n'   "$(find . -name "$decomp" | wc -l | tr -d ' ') hit(s)"
printf '   the two patterns differ: %s vs %s\n' \
  "$(printf '%s' "$comp" | xxd -p)" "$(printf '%s' "$decomp" | xxd -p)"
echo
echo "   find compares BYTES. The two patterns are different byte strings, so"
echo "   at most one of them can match -- and which one matches depends on"
echo "   what the filesystem stored, not on what you typed."
echo
echo "WHY THAT IS A MAC-SPECIFIC TRAP"
echo "   On Linux the kernel stores the bytes you handed it, so the NFC pattern"
echo "   finds the NFC file and that is the end of it."
echo "   On macOS the filesystem may DECOMPOSE the name on the way in -- HFS+"
echo "   did this always, APFS normalizes on comparison -- so a file created"
echo "   with c3 a9 can be listed back as 65 cc 81. Your shell then completes"
echo "   the name correctly, cat opens it, and find -name with the composed"
echo "   spelling finds nothing. Same machine, same second, one tool comparing"
echo "   bytes and another comparing through a normalizing layer."
echo
echo "WHAT WORKS ON EITHER"
printf '   find . -name "caf*"     %s hit(s)   -- a pattern that avoids the letter\n' \
  "$(find . -name 'caf*' | wc -l | tr -d ' ')"
echo "   Or normalize both sides before comparing, in a language that can:"
echo "       python3 -c \"import unicodedata,sys;print(unicodedata.normalize('NFC',sys.argv[1]))\""
echo
echo "THE GENERAL SHAPE"
echo "   A filename is a bag of bytes with two forbidden values, 00 and 2f. It"
echo "   is not text, it has no declared encoding, and every tool that treats"
echo "   it as text has quietly chosen one. find chose bytes -- which is the"
echo "   defensible choice, and still surprises you."
