#!/usr/bin/env bash
# The first two bytes, and whether your file runs at all.
#
# Four scripts that differ only in bytes nothing draws. One runs. One dies
# naming an interpreter that plainly exists. One runs anyway and exits 0,
# which is the worst of the three.
#
# The shells' error TEXT is not recorded here: it differs between bash 3.2
# (macOS) and bash 5.x (Ubuntu), so stderr is dropped and the exit status —
# which does not differ — is printed instead. The messages are on the page,
# in a dated fence.
#
# Run:  bash the_first_two_bytes_sh.sh
set -u

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

# Octal escapes, not \x — \x is a bash extension and this file is about
# writing exact bytes, so it should not use a spelling that is not portable.
printf '#!/bin/sh\necho "  I ran"\n'             > plain.sh   # well formed
printf '\357\273\277#!/bin/sh\necho "  I ran"\n' > bom.sh     # EF BB BF in front
printf '#!/bin/sh\r\necho "  I ran"\r\n'         > crlf.sh    # CR before each LF
printf 'echo "  I ran"\n'                        > none.sh    # no #! at all
chmod +x plain.sh bom.sh crlf.sh none.sh

echo "1. FOUR FILES, AND THE BYTES AT OFFSET 0"
for f in plain.sh bom.sh crlf.sh none.sh; do
    printf '   %-9s %s\n' "$f" "$(head -c 8 "$f" | xxd -p)"
done
echo "   The kernel reads THIS, and only this. Not the name, not the extension,"
echo "   not what file(1) guesses. 23 21 is the ASCII for #!"

echo
echo "2. WHERE THE #! ACTUALLY IS"
show "head -c 2 plain.sh | xxd -p"
show "head -c 5 bom.sh | xxd -p"
echo "   In bom.sh the #! is still there — at offset 3. The kernel does not go"
echo "   looking for it, so three bytes of byte-order mark are three bytes too many."

echo
echo "3. RUNNING THEM"
for f in plain.sh bom.sh crlf.sh none.sh; do
    out=$(./"$f" 2>/dev/null); st=$?
    # The exact NONZERO status is not printed, because it is not a property of
    # the file: Apple's /bin/bash answers 126 where bash 3.2.57 on Linux -- the
    # same version -- answers 127, and so do zsh, fish and dash on macOS. The
    # three ZEROS are the finding, and they are the same everywhere.
    if [ "$st" -eq 0 ]; then verdict="exit=0"; else verdict="exit=nonzero"; fi
    printf '   ./%-9s %-12s stdout=%s\n' "$f" "$verdict" "${out:-(nothing)}"
done
echo "   Three of the four printed something. Only ONE of those three is a"
echo "   script the kernel agreed to run: for bom.sh and none.sh the kernel"
echo "   refused, and the SHELL caught the refusal and ran the file itself."
echo "   That rescue is why a broken file passes a test that checks exit status."
echo "   (bom.sh and none.sh exit 0 on every shell and both platforms. crlf.sh's"
echo "   nonzero value is 126 on Apple's bash and 127 nearly everywhere else, so"
echo "   it is a fact about your shell, not about the file, and is not printed.)"

echo
echo "4. THE BYTE THAT KILLED crlf.sh"
show "cat -vet crlf.sh"
echo "   ^M is the CR. The kernel found the #!, then read to the LF — so the"
echo "   interpreter it went looking for is /bin/sh followed by a CR, which is"
echo "   a filename nothing on the system has. Hence an error about a missing"
echo "   file, for a file that is right there."

echo
echo "5. THE INTERPRETER PATH, AS THE KERNEL BUILDS IT"
show "sed -n '1s/^#!//p' plain.sh | cat -vet"
show "sed -n '1s/^#!//p' crlf.sh  | cat -vet"
echo "   Same nine characters on screen. One of them is ten bytes."

echo
echo "6. THE FIX, AND HOW TO CHECK IT AFTERWARDS"
# tr names the byte in octal and asks nothing of a regex grammar. s/\r$// would
# also work -- BSD, GNU and busybox sed all three strip it -- but \r is not in
# POSIX, which leaves a backslash before an ordinary character undefined in a
# BRE, so all three are extending the standard and merely agreeing. sed -i is
# the real portability trap: it takes a backup suffix on BSD and not on GNU.
show "tr -d '\\015' < crlf.sh > fixed.sh && chmod +x fixed.sh && ./fixed.sh"
show "head -c 12 fixed.sh | xxd -p"
echo "   Nothing on screen changed when it was broken and nothing changed when"
echo "   it was fixed. The dump is the only view that ever showed the defect."
