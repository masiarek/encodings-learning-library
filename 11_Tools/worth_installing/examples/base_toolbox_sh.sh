#!/usr/bin/env bash
# What the tools you ALREADY have answer, on the four files the optional tools
# are measured against on this page. Read this first: it is the baseline, and
# every install is only worth what it adds to it.
#
# Run:  bash base_toolbox_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251 1\342\202\254\n' > utf8.txt      # café 1€, UTF-8
printf 'caf\351\n'                   > latin1.txt    # café, Latin-1: e9
printf 'Preis 100\200\n'             > cp1252.txt    # € as Windows-1252's 0x80
printf 'dos line\r\nunix line\nlast\r\n' > mixed.txt # two CRLF lines, one LF

echo "1. WHAT IS IN THESE FILES"
for f in utf8.txt latin1.txt cp1252.txt mixed.txt; do
  printf '   %-11s %s\n' "$f" "$(xxd -p "$f")"
done

echo
echo "2. file --mime-encoding — THE ANSWER YOU ALREADY HAVE"
echo '$ file --mime-encoding utf8.txt latin1.txt cp1252.txt'
file --mime-encoding utf8.txt latin1.txt cp1252.txt
echo "   Three files, three qualities of answer. utf-8 is an inference from"
echo "   valid structure and is nearly always right. iso-8859-1 is a proof of a"
echo "   NEGATIVE — 'not valid UTF-8' — with a plausible 8-bit table named, and"
echo "   file cannot tell 8859-1 from 8859-2 or 8859-15 because on this byte"
echo "   they agree. unknown-8bit is the honest surrender: 0x80 is unassigned in"
echo "   every ISO 8859 table, so file will not name one. uchardet names it."

echo
echo "3. xxd's TEXT COLUMN — ONE GLYPH FOR EVERY PROBLEM"
echo '$ printf "caf\\303\\251 1\\342\\202\\254\\n\\000A" | xxd'
printf 'caf\303\251 1\342\202\254\n\000A' | xxd
echo "   Look at the right-hand column: caf.. 1.....A. Five dots, standing in"
echo "   for two continuation bytes of é, three of €, a newline and a NUL. They"
echo "   are four completely different kinds of byte and xxd draws them all the"
echo "   same. That is what hexyl fixes — see the page."

echo
echo "4. iconv AS A YES/NO VALIDATOR — THE ONE PORTABLE USE"
for f in utf8.txt latin1.txt cp1252.txt; do
  if iconv -f UTF-8 -t UTF-8 "$f" >/dev/null 2>&1; then
    printf '   %-11s valid UTF-8\n' "$f"
  else
    printf '   %-11s NOT valid UTF-8\n' "$f"
  fi
done
echo "   That is the whole of what the base toolbox can prove. Which table the"
echo "   invalid two are in is not a question iconv answers — it is the question"
echo "   uchardet exists for, and the answer is still a guess."

echo
echo "5. LINE ENDINGS WITHOUT dos2unix"
echo '$ cat -vet mixed.txt'
cat -vet mixed.txt
echo -n '   lines ending CRLF : '; grep -c $'\r$' mixed.txt || true
echo -n '   lines in total    : '; wc -l < mixed.txt | tr -d ' '
echo '$ sed "s/\r$//" mixed.txt | cat -vet'
sed 's/\r$//' mixed.txt | cat -vet
echo "   ^M\$ is a CRLF line and \$ alone is an LF line, so cat -vet is the free"
echo "   diagnosis and sed is the free repair. dos2unix -i gives you the same"
echo "   counts in one line, and dos2unix does the repair without a regex you"
echo "   have to get right — which matters on the day the file is UTF-16."
