#!/usr/bin/env bash
# Answer key: three scripts that differ only in bytes you cannot see.
#
# Only EXIT STATUS is recorded, never the kernel's or the shell's message:
# "bad interpreter", "cannot execute" and the rest are worded differently by
# every platform and shell, and the status is the part that is the same.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

printf '#!/bin/sh\necho ran\n'            > good.sh
printf '\357\273\277#!/bin/sh\necho ran\n' > bom.sh      # a UTF-8 BOM in front of #!
printf '#!/bin/sh\r\necho ran\r\n'         > crlf.sh     # DOS line endings
chmod +x good.sh bom.sh crlf.sh

printf '   %-10s %-26s %s\n' file 'first 6 bytes' 'shebang line, as bytes'
for f in good.sh bom.sh crlf.sh; do
  printf '   %-10s %-26s %s\n' "$f" "$(head -c6 "$f" | xxd -p)" "$(head -1 "$f" | xxd -p)"
done
echo
echo "RUN THEM DIRECTLY -- this is the kernel reading the first two bytes"
# The STATUS of a failed exec is not portable: a missing interpreter is 126
# on a Mac and 127 on Ubuntu, both correct readings of "could not run it".
# Record the verdict, and name the two numbers in the prose instead.
verdict() { case $1 in 0) echo "ran";; 126|127) echo "did NOT run (126 or 127)";; *) echo "exit $1";; esac; }
for f in good.sh bom.sh crlf.sh; do
  st=0; ./"$f" >/dev/null 2>&1 || st=$?
  printf '   ./%-10s %s\n' "$f" "$(verdict $st)"
done
echo
echo "NOW HAND THE SAME FILES TO sh, WHICH DOES NOT LOOK AT THE FIRST TWO BYTES"
for f in good.sh bom.sh crlf.sh; do
  st=0; sh "$f" >/dev/null 2>&1 || st=$?
  printf '   sh %-10s %s\n' "$f" "$(verdict $st)"
done
echo
echo "WHAT HAPPENED, LINE BY LINE"
echo
echo "good.sh   23 21 is '#!', so the kernel reads the rest of the line as an"
echo "          interpreter path and execs /bin/sh. Nothing else about the file"
echo "          matters at this point -- not the name, not the extension."
echo
echo "bom.sh    starts ef bb bf. The kernel compares the first TWO bytes"
echo "          against 0x23 0x21, they do not match, so the file has no"
echo "          shebang and execve fails with ENOEXEC -- and yet it exited 0."
echo "          That is the shell catching the failure and re-running the file"
echo "          with itself, a POSIX fallback older than the shebang. So three"
echo "          bytes nothing draws took the kernel out of the loop, the script"
echo "          still ran, and no status anywhere records that anything"
echo "          unusual happened. Under a different interpreter -- python3,"
echo "          awk -- there is no fallback and it simply does not run."
echo
echo "          The status it fails with is itself platform-dependent -- 126"
echo "          on macOS, 127 on Ubuntu, measured 2026-09-07 -- which is why"
echo "          the table above records a verdict and not a number. A script"
echo "          testing for one of the two is testing its own machine."
echo
echo "crlf.sh   the shebang matches, so the kernel takes the rest of the line"
echo "          -- and the line ends 0d 0a, so the interpreter it looks for is"
echo "          '/bin/sh' with a CARRIAGE RETURN on the end. There is no such"
echo "          file. The error names /bin/sh, which is present and correct,"
echo "          and the invisible byte is the whole problem."
echo
echo "THE PART THAT CATCHES PEOPLE"
echo "   Look at the second block. Both broken files RUN under sh, because the"
echo "   shell was told which interpreter to use and never consults the first"
echo "   two bytes. So the same file fails one way and works the other, and a"
echo "   CI job that invokes 'sh script.sh' passes while the deployed cron"
echo "   entry that runs './script.sh' fails."
echo
echo "   crlf.sh under sh is worth its own line: it runs, and every command in"
echo "   it receives an argument with a trailing 0d. That usually still exits 0"
echo "   -- which is the worst of the three outcomes, because nothing at all"
echo "   reports it."
