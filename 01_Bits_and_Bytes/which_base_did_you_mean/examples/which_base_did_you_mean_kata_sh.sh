#!/usr/bin/env bash
# Answers to the kata on "Which base did you mean?".
#
# Run:  bash which_base_did_you_mean_kata_sh.sh
#
# Every answer is produced rather than asserted, so the fold on the page cannot
# drift from what the shell does. Nothing here depends on the machine: the file
# is built in a scratch directory and every tool used reads a leading zero the
# same way on macOS and on Ubuntu.
set -eu

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"
printf '0123456789abcdef0123456789ABCDEF................' > q.bin

echo "1. THREE SPELLINGS IN \$(( ))"
printf '   %-16s = %s\n' '$(( 0x10 ))' "$((0x10))" '$(( 010 ))' "$((010))" '$(( 10#010 ))' "$((10#010))"
echo "   Sixteen, eight, ten. The first says its base, the second says it in a"
echo "   character you can miss, and the third says the base that needs saying"
echo "   precisely because it is the one everybody assumes."

echo
echo "2. SEEKING TO THE ROW LABELLED 00000020"
xxd -g 4 q.bin | sed 's/^/   /'
echo "   The third row's label is 00000020, and that is hex, so it is byte 32."
printf '   %-14s %s\n' 'xxd -s 0x20' "$(xxd -s 0x20 -l 4 -p q.bin)" \
                        'xxd -s 32' "$(xxd -s 32 -l 4 -p q.bin)" \
                        'xxd -s 20' "$(xxd -s 20 -l 4 -p q.bin)" \
                        'xxd -s 020' "$(xxd -s 020 -l 4 -p q.bin)"
echo "   The first two are the same place. -s 20 is decimal twenty, twelve bytes"
echo "   early; -s 020 is octal sixteen, which lands on the row above. Three"
echo "   spellings of \"twenty-ish\", three different bytes, and no complaint from"
echo "   any of them. Type the 0x and the question does not arise."

echo
echo "3. THE SAME TEST, TWO BUILTINS"
if [ 010 -eq 8 ]; then a=true; else a=false; fi
if [[ 010 -eq 8 ]]; then b=true; else b=false; fi
printf '   %-20s %s\n' '[ 010 -eq 8 ]' "$a" '[[ 010 -eq 8 ]]' "$b"
echo "   [[ ]] evaluates its operands arithmetically, so 010 is octal eight and the"
echo "   test passes. [ ] reads them in base 10, so 010 is ten and it fails."

echo
echo "4. FOUR CHARACTERS, TWO FLAGS"
printf '   %-16s %s\n' 'xxd -s 010' "$(xxd -s 010 -l 4 -p q.bin)   (seeks to byte 8)"
printf '   %-16s %s\n' 'head -c 010' "$(head -c 010 q.bin | tr -d '\n')   (reads ten bytes)"
echo "   One of them called strtol with base 0 and the other with base 10. Nothing"
echo "   on either man page's synopsis line tells you which, and both are ordinary"
echo "   choices for a tool to make."

echo
echo "5. THE NUMBER YOU HAVE MEMORISED IS OCTAL"
printf '   %-24s %s\n' 'chmod 644 means octal' "$(printf '0%o = %d decimal\n' 420 420)"
printf '   %-24s %s\n' 'so decimal 644 would be' "$(printf '0%o octal\n' 644)"
: > f; chmod 644 f; printf '   %-24s %s\n' 'and chmod 644 gives' "$(ls -l f | cut -c1-10)"
echo "   rw-r--r-- is 420 as a decimal number. Nobody writes it that way, because"
echo "   chmod's field has exactly one base and no syntax for saying so -- which is"
echo "   the cleanest case on the page: an invisible default nobody trips over,"
echo "   because it never varies and the tool refuses the digits 8 and 9."
