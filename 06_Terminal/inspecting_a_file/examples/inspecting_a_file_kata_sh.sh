#!/usr/bin/env bash
# Answer key: five readings of one file, and the one column that is the file.
#
# od -a's names and hexdump's default word order differ per platform, so this
# key runs neither in a form whose output it records: it records xxd, which is
# one program everywhere, and states what the other two do in prose. That
# restriction IS the lesson -- if a dump's output depends on the machine, it
# was never showing you only the file.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

printf 'Hi\303\251\t\n' > f

echo "THE FILE"
printf '   %s bytes: %s\n' "$(wc -c < f | tr -d ' ')" "$(xxd -p < f)"
echo
echo "1. xxd -- one byte at a time, in file order"
xxd f | sed 's/^/   /'
echo "   The middle column is the file. Nothing here was reordered, decoded or"
echo "   guessed."
echo
echo "2. THE TEXT COLUMN IS ALREADY A READING"
echo "   Hi.... -- FOUR of the six bytes drew as dots. c3 and a9 are one"
echo "   letter and the column shows two dots for it; 09 and 0a add two more."
echo "   The column tests each byte against ASCII on its own, so it can never"
echo "   show you a character that took more than one byte."
echo
echo "3. cat -v -- the same bytes respelled in ASCII"
cat -v f | sed 's/^/   /'
echo "   M-C M-) is c3 a9, and ^I is the tab. Nothing is lost and nothing is"
echo "   decoded: it is a pure respelling, which is why it survives being"
echo "   pasted into an email and xxd does not."
echo
echo "4. WHAT THIS KEY DELIBERATELY DOES NOT RUN"
echo "   od -a  names the low bytes -- ht, nl, sp -- and the names it uses"
echo "          differ between the BSD and GNU builds. Its default is octal"
echo "          WORDS at octal offsets, which is a C type, not a file."
echo "   hexdump  with no flags prints 16-bit words in your CPU's byte order,"
echo "          so 'Hi' comes out as 6948 on a little-endian machine. The bytes"
echo "          were reordered to suit an integer that is not in the file."
echo "   Both are recorded nowhere in this key because their output is a fact"
echo "   about the machine. Use hexdump -C, or xxd, when you need the file."
echo
echo "5. file -- the only one that is guessing"
echo "   It reads the first bytes and matches a table. On this file it will say"
echo "   something about text; on a file one byte longer it might say something"
echo "   else. A guess is useful and it is not evidence."
echo
echo "THE RULE"
echo "   Exactly one column in this whole page is the file: the hex, printed"
echo "   one byte at a time, in file order. Everything else -- the text column,"
echo "   cat -v, od's names, file's verdict -- is a reading, and every reading"
echo "   has already decided something on your behalf."
