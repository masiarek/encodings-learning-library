#!/usr/bin/env bash
# sed on text that is not ASCII. Everything here runs in the C locale, which is
# what the library's runner pins, and is byte-identical on macOS and Ubuntu.
# What changes with the locale, and what the two seds do with undecodable
# bytes, is on the page in a dated fence.
#
# Run:  bash sed_matches_patterns_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251 na\303\257ve\n' > two.txt        # café naïve
printf 'caf\303\251\n' > cafe.txt                    # café
printf 'dos\r\nunix\n' > crlf.txt
printf 'no trailing newline' > nonl.txt

echo "1. THE ONE THING tr CANNOT DO"
echo '$ cat two.txt'
cat two.txt
echo '$ xxd -p two.txt'
xxd -p two.txt
echo '$ tr -d "é" < two.txt | xxd -p          # the byte-set tool'
tr -d 'é' < two.txt | xxd -p
echo '$ sed "s/é//" < two.txt | xxd -p        # the pattern tool'
sed 's/é//' < two.txt | xxd -p
echo "   Same request, two results. tr was given the byte SET {c3, a9} and"
echo "   deleted both bytes wherever it met them, so it took the c3 out of the"
echo "   middle of ï and left an orphan af. sed was given the two-byte SEQUENCE"
echo "   c3 a9 and matched it as a unit, so naïve is untouched and both words"
echo "   are still valid UTF-8. That is the whole reason to reach for sed."
echo "   Note this works even here, in the C locale, where sed has no idea what"
echo "   a character is: a pattern is a sequence of bytes and so is é."

echo
echo "2. BUT '.' IS STILL A BYTE IN THIS LOCALE"
echo '$ sed "s/./X/g" cafe.txt'
sed 's/./X/g' cafe.txt
echo "   Four characters on screen, five X. The dot means one byte here. In a"
echo "   UTF-8 locale the same command prints four — both seds agree about that,"
echo "   so this one is the locale talking, not the implementation."

echo
echo "3. y/// IS tr INSIDE sed, AND IT INHERITS tr'S PROBLEM"
echo '$ sed "y/é/e/" cafe.txt'
if sed 'y/é/e/' cafe.txt 2>/dev/null; then
  echo "   (it ran)"
else
  echo "   (refused — exit $?)"
fi
echo "   y transliterates character by character, which in this locale means"
echo "   byte by byte: 'é' is two bytes and 'e' is one, so the two sides are"
echo "   different lengths and sed will not guess. Both seds refuse; they word"
echo "   the complaint differently, which is why only the exit status is shown."
echo "   The refusal is the good outcome — compare tr, which just did it."

echo
echo "4. THE CRLF REPAIR, WHICH IS THE COMMONEST REAL USE"
echo '$ cat -vet crlf.txt'
cat -vet crlf.txt
echo '$ sed "s/\r$//" crlf.txt | cat -vet'
sed 's/\r$//' crlf.txt | cat -vet
echo "   ^M\$ is a CRLF line and \$ alone is an LF line. The pattern is anchored"
echo "   to the end on purpose: an unanchored s/\\r// would also delete a CR"
echo "   sitting legitimately inside a quoted CSV field."

echo
echo "5. sed DOES NOT ADD A TRAILING NEWLINE"
echo '$ xxd -p nonl.txt'
xxd -p nonl.txt
echo '$ sed "s/trailing/final/" nonl.txt | xxd -p'
sed 's/trailing/final/' nonl.txt | xxd -p
echo "   Neither dump ends in 0a. sed passed the missing newline through rather"
echo "   than tidying it up, and both seds agree. That matters because a lot of"
echo "   tools do not — and a file that gains a byte in a pipeline is a file"
echo "   whose checksum has changed."

echo
echo "6. THE TWO SPELLINGS OF EDIT-IN-PLACE"
echo "   BSD sed  : sed -i '' 's/x/y/' file      # the '' is a required argument"
echo "   GNU sed  : sed -i    's/x/y/' file      # and this FAILS on BSD"
echo "   portable : sed 's/x/y/' file > tmp && mv tmp file"
echo "   -i is the one sed flag with no portable spelling. On BSD the argument"
echo "   is the backup suffix and it is mandatory; on GNU it is optional and"
echo "   attached (-i.bak). A script that uses bare -i is a script that works"
echo "   on Linux and silently writes a file called 's/x/y/' on a Mac."
