#!/usr/bin/env bash
# What a shell script can find out about its own stdout, and what it cannot.
#
# Read the first section before anything else: this script is running with its
# output captured, so every answer it gets is the PIPED one. That is not a
# limitation of the example, it is the subject of the page — and it is why the
# Python example beside this one opens a real pty instead of asking.
#
# Everything recorded here was byte-identical on macOS 26.6.2 and ubuntu:24.04,
# grep's colour escapes included.
#
# Run:  bash pipe_is_not_a_terminal_sh.sh
set -u
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

esc() { tr -dc '\033' | wc -c | tr -d ' '; }   # how many ESC bytes came through

echo "1. THE TEST EVERY SHELL HAS, AND THE ANSWER IT GIVES HERE"
for fd in 0 1 2; do
  if [ -t "$fd" ]; then a="a terminal"; else a="NOT a terminal"; fi
  printf '   [ -t %s ]  fd %s is %s\n' "$fd" "$fd" "$a"
done
echo "   All three, because a test runner captured every one of them. Run this"
echo "   script by hand and fd 1 and 2 change their answer while fd 0 may not."
echo "   [ -t N ] is the shell's isatty(): one syscall, three characters, and"
echo "   the thing dozens of programs quietly branch on before they print."

echo
echo "2. WHAT A PROGRAM DOES WITH THAT ANSWER: COLOUR"
printf 'alpha\nbeta\n' > words.txt
for mode in auto always never; do
  n=$(grep --color=$mode 'al' words.txt | esc)
  b=$(grep --color=$mode 'al' words.txt | od -An -tx1 | tr -s ' ' | tr -d '\n' | sed 's/^ *//; s/ *$//')
  printf '   --color=%-7s ESC bytes: %s   output: %s\n' "$mode" "$n" "$b"
done
echo "   Same match, three answers. Under 'auto' grep asked [ -t 1 ], found a"
echo "   pipe, and shipped plain text — which is why colour disappears the"
echo "   moment you add '| less' and why nobody's log file is full of escape"
echo "   codes. 'always' is the override, and it is what you want when the"
echo "   thing on the other end of the pipe is a pager that understands them."

echo
echo "3. WHAT 'ALWAYS' ADDED, AND WHY IT IS NOT TEXT"
grep --color=always 'al' words.txt > coloured.txt
printf '   cat -v: %s\n' "$(cat -v coloured.txt | tr -d '\n')"
printf '   bytes : %s\n' "$(od -An -tx1 < coloured.txt | tr -s ' ' | tr -d '\n' | sed 's/^ *//; s/ *$//')"
grep --color=never 'al' words.txt > plain.txt
printf '   wc -c : %s bytes on the wire for %s bytes of text — %s bytes of instruction\n' \
       "$(wc -c < coloured.txt | tr -d ' ')" "$(wc -c < plain.txt | tr -d ' ')" \
       "$(( $(wc -c < coloured.txt) - $(wc -c < plain.txt) ))"
echo "   1b is ESC. Everything between it and the letter 'm' is an instruction"
echo "   to the terminal, not content — so a coloured line is longer than it"
echo "   looks, sorts differently, and will not match a regex anchored with ^."
echo "   That is the cost of letting a display decision into the byte stream,"
echo "   and it is the reason 'auto' is the default rather than 'always'."

echo
echo "4. THE IDIOM TO WRITE IN YOUR OWN SCRIPTS"
cat <<'IDIOM'
     if [ -t 1 ]; then colour=always; else colour=never; fi
     grep --color=$colour "$pattern" "$file"
IDIOM
echo "   Three lines, and it is the whole of good behaviour here: decide from"
echo "   the file descriptor, never from a guess about who is running you."
echo "   The mirror of it is to always provide the override, because the one"
echo "   thing [ -t 1 ] cannot see is a human on the far side of a pager."

echo
echo "5. WHAT THE SHELL CANNOT DO"
echo "   It cannot make a terminal. There is no builtin, and the one tool that"
echo "   would — script(1) — takes incompatible arguments on the two platforms"
echo "   and each rejects the other's spelling. That table is on the page."
echo "   So a portable script cannot test its own both-branches behaviour,"
echo "   which is exactly the gap the Python example next door fills with the"
echo "   pty module. A shell script can ask the question; it cannot arrange"
echo "   for the other answer."
