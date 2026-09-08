#!/usr/bin/env bash
# Kata solution: three files that all report us-ascii, and the tool that can
# tell them apart.
#
# Everything here is --mime-encoding and exit statuses, both of which were
# identical on file-5.41 / 5.44 / 5.45 and on Apple and GNU iconv.
#
# Run:  bash file_guesses_kata_sh.sh
set -u
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

pad() { head -c "$1" /dev/zero | tr '\000' 'a'; }

printf 'plain ascii\n'                        > a_really.txt
{ pad 65536; printf 'caf\303\251\n'; }        > b_utf8_late.txt
{ pad 65536; printf 'caf\351\n'; }            > c_latin1_late.txt

echo "1. THREE FILES, ONE VERDICT"
for f in a_really.txt b_utf8_late.txt c_latin1_late.txt; do
  printf '   %-18s %8s bytes   file says %s\n' "$f" "$(wc -c < "$f" | tr -d ' ')" \
         "$(file -b --mime-encoding "$f")"
done
echo "   Only the first one is ASCII. The other two hold a non-ASCII character"
echo "   past byte 65536, which is outside the window file(1) reads, so all"
echo "   three get the same answer and two of them are wrong."

echo
echo "2. THE TOOL THAT READS THE WHOLE FILE"
for f in a_really.txt b_utf8_late.txt c_latin1_late.txt; do
  iconv -f US-ASCII -t UTF-8 "$f" >/dev/null 2>&1; a=$?
  iconv -f UTF-8    -t UTF-8 "$f" >/dev/null 2>&1; u=$?
  printf '   %-18s all ASCII? exit=%s     valid UTF-8? exit=%s\n' "$f" "$a" "$u"
done
echo "   iconv converts every byte or stops, so its answer is about the file"
echo "   rather than about a prefix. Read the two columns together: 0/0 is"
echo "   ASCII, 1/0 is UTF-8 with something above 127 in it, 1/1 is neither —"
echo "   an 8-bit table, and no tool in the terminal can tell you which."
echo "   Note the FIRST command: it is -f US-ASCII -t UTF-8, not the -f X -t X"
echo "   form this library uses to validate UTF-8. Apple's iconv does not"
echo "   refuse a high byte when ASCII is named on BOTH sides — it substitutes"
echo "   a question mark and exits 0. Naming a different target avoids that"
echo "   path and the two platforms agree. The measurement is on the page."

echo
echo "3. WHICH ANSWER WAS EVIDENCE"
printf '\377\376A\000' > bom.bin
printf '   %-30s %s\n' "ff fe 41 00" "$(file -b --mime-encoding bom.bin)"
printf '   %-30s %s\n' "the three files above" "us-ascii, three times"
echo "   The BOM row is the only claim on this page that rests on something"
echo "   written IN the file. us-ascii, utf-8 and iso-8859-1 are all read OFF"
echo "   the bytes — the first two by validating, the third by failing to."
echo "   A guess that reads 64 KiB is still a guess; a guess that reads the"
echo "   whole file is a slower guess. Only a mark, a manifest, a Content-Type"
echo "   header or a contract makes it a fact."

echo
echo "4. WHAT TO DO ABOUT IT"
echo "   * Ask --mime-encoding, never the English wording: the prose moved"
echo "     the word 'executable' between file 5.41 and 5.44 and the MIME"
echo "     output did not change at all."
echo "   * Use file(1) to triage and iconv to decide."
echo "   * If you control the producer, write the encoding down somewhere a"
echo "     program can read: that is the only way the answer stops being an"
echo "     inference."
