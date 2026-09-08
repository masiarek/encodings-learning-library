#!/usr/bin/env bash
# Answer key: two stages, and which one -z is.
# rg is not installed on the CI runners, so the searching half is done with grep
# -- the stage question is the same and the answer is not about which grep.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'hello\n' > plain.txt
gzip -c plain.txt > plain.txt.gz
printf 'hello\n' | iconv -f UTF-8 -t UTF-32LE > wide.txt
gzip -c wide.txt > wide.txt.gz

echo "TWO FILES, EACH GZIPPED"
printf '   plain.txt   %s\n' "$(xxd -p < plain.txt)"
printf '   wide.txt    %s   (UTF-32LE: four bytes per character)\n' "$(xxd -p < wide.txt)"
echo
echo "SEARCH THE COMPRESSED FILES"
printf '   zgrep hello plain.txt.gz   %s hit(s)\n' "$(zgrep -c hello plain.txt.gz 2>/dev/null || true)"
printf '   zgrep hello wide.txt.gz    %s hit(s)\n' "$(zgrep -c hello wide.txt.gz 2>/dev/null || true)"
echo
echo "WHY THE SECOND ONE FINDS NOTHING"
printf '   decompressed, wide.txt is %s\n' "$(gzip -dc wide.txt.gz | xxd -p)"
echo "   The decompression worked perfectly. What came out is UTF-32, in which"
echo "   'hello' is spelled 68 00 00 00 65 00 00 00 ... -- and the pattern"
echo "   'hello' is five consecutive bytes. They are not in the file."
echo
echo "THE TWO STAGES, AND WHY THE ORDER SETTLES IT"
echo "   1. UNWRAP   gzip -> a byte stream.  This is what -z and zgrep do."
echo "   2. DECODE   bytes -> characters.    This is the locale/BOM machinery,"
echo "      and it runs afterwards, exactly as it would on an uncompressed file."
echo "   A container is not an encoding. Removing the container hands the"
echo "   encoding problem to the next stage untouched -- so anything that was"
echo "   unreadable before compression is still unreadable after -z."
echo
echo "THE STAGE THAT CAN FIX IT"
printf '   iconv -f UTF-32LE -t UTF-8, then search: %s hit(s)\n' \
  "$(gzip -dc wide.txt.gz | iconv -f UTF-32LE -t UTF-8 | grep -c hello)"
echo "   That is what rg --pre buys: a command of YOUR choosing that runs"
echo "   before stage 2, so you can put a decode there, or a pdftotext, or"
echo "   anything else that turns a file into searchable bytes."
echo "   -z is a fixed list of decompressors; --pre is a general escape hatch,"
echo "   and it is slower because it forks a process per file."
