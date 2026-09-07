#!/usr/bin/env bash
# The stray 0d, and the three commands that find it.
#
# A file with the wrong line ending is not corrupt and does not look wrong.
# It looks EXACTLY right: cat prints the same characters, an editor shows the
# same lines, a paste into a chat window is identical. The difference is one
# byte per line, and everything on this page is a way of making that byte
# visible or getting rid of it.
#
# No carriage return is ever printed raw here. A CR moves the cursor to column
# zero, so printing one would erase the label in front of it -- the byte this
# page is about is the one byte that cannot appear in its own output. Every
# sighting below is hex, or cat -vet's ^M.
#
# Run:  bash crlf_vs_lf_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
say()  { printf '\n%s\n%s\n' "$1" "------------------------------------------------------------------------"; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'one\ntwo\n'     > unix.txt
printf 'one\r\ntwo\r\n' > win.txt
printf 'one\rtwo\r'     > mac.txt
printf 'one\r\ntwo\n'   > mixed.txt

say "1. FOUR FILES, AND THE ONE COMMAND THAT NAMES THEM"
for f in unix.txt win.txt mac.txt mixed.txt; do
    printf '  %-10s %s\n' "$f" "$(file -b "$f")"
done
printf '\n  file(1) reads the ending straight out of the bytes and says so in\n'
printf '  words. It is the fastest question to ask about a file somebody sent\n'
printf '  you, and the last line shows it will tell you when a file has BOTH.\n'

show "xxd unix.txt"
show "xxd win.txt"
printf '  0d 0a against 0a. One extra byte per line, at the end of each line,\n'
printf '  and 0d is CR -- the carriage return that was a separate motion on a\n'
printf '  teletype. Unix kept the line feed; DOS kept both; Windows inherited\n'
printf '  it and so did every protocol written in the 1980s.\n'

say "2. WHAT THE SCREEN WILL NOT SHOW YOU"
printf '\n$ cat win.txt          (piped through cat -vet, which draws the CR)\n'
cat -vet win.txt | sed 's/^/  /'
printf '\n  Without -vet, cat prints "one" and "two" and you would swear the file\n'
printf '  was fine. ^M is the CR, $ is the LF, and the pair at the end of every\n'
printf '  line is the signature of a Windows file. That ^M is what vim shows\n'
printf '  you, for the same reason -- it is caret notation, not a warning.\n'

show "wc -l < win.txt | tr -d ' '"
show "wc -l < mac.txt | tr -d ' '"
printf '  Two lines, and zero. wc -l counts 0a bytes and the classic-Mac file\n'
printf '  has none at all, so a perfectly readable two-line file reports no\n'
printf '  lines -- the same arithmetic as a missing trailing newline, one byte\n'
printf '  along.\n'

say "3. THREE PIPELINES THAT QUIETLY GIVE THE WRONG ANSWER"
printf '  grep -c "^two$"     unix %-6s win %s\n' \
    "$(grep -c '^two$' unix.txt || true)" "$(grep -c '^two$' win.txt || true)"
printf '  a CSV field, cut    unix %-6s win %s\n' \
    "$(printf '1,Ada,Y\n'   | cut -d, -f3 | tr -d '\n' | xxd -p)" \
    "$(printf '1,Ada,Y\r\n' | cut -d, -f3 | tr -d '\n' | xxd -p)"
v=$(printf '1,Ada,Y\r\n' | cut -d, -f3)
if [ "$v" = "Y" ]; then r="match"; else r="NO MATCH"; fi
printf '  [ "$v" = "Y" ]      %s\n' "$r"
printf '\n  The anchored grep finds nothing, because $ anchors after the CR, not\n'
printf '  before it. cut hands back 59 0d where you expected 59. And the shell\n'
printf '  compares two strings that print identically and are not equal. Every\n'
printf '  one of those exits 0. Nothing is reported; a report just comes out\n'
printf '  empty, or a lookup silently matches nothing.\n'

say "4. STRIPPING IT: TWO COMMANDS THAT ARE NOT THE SAME"
show "tr -d '\r' < win.txt | xxd"
show "sed 's/\r\$//' win.txt | xxd"
printf '  Same answer here, and they are not the same command. tr deletes\n'
printf '  EVERY 0d in the file, wherever it sits. sed deletes one only where a\n'
printf '  line ends. On a file whose CRs are all line endings that is the same\n'
printf '  file; on one with a CR in the middle of a line it is not:\n'
printf '\n$ printf %s | tr -d %s | xxd\n' "'a\\rb\\r\\n'" "'\\r'"
printf 'a\rb\r\n' | tr -d '\r' | xxd | sed 's/^/  /'
printf '\n$ printf %s | sed %s | xxd\n' "'a\\rb\\r\\n'" "'s/\\r\$//'"
printf 'a\rb\r\n' | sed 's/\r$//' | xxd | sed 's/^/  /'
printf '\n  tr produced "ab" and sed produced "a", CR, "b". Which one you want\n'
printf '  depends on whether a CR that is not a line ending is damage or data,\n'
printf '  and only you know that. Reach for sed when the file is text somebody\n'
printf '  saved on Windows, and for tr when you want every CR gone.\n'
printf '\n  Now the case where NEITHER is right. A CSV may hold a real line break\n'
printf '  inside a quoted field, and both of these are line-oriented tools that\n'
printf '  split on 0a -- so to both of them that break is just another line\n'
printf '  ending:\n'
printf '\n$ printf %s | tr -d %s | xxd\n' "'1,\"a\\r\\nb\"\\r\\n'" "'\\r'"
printf '1,"a\r\nb"\r\n' | tr -d '\r' | xxd | sed 's/^/  /'
printf '\n$ printf %s | sed %s | xxd\n' "'1,\"a\\r\\nb\"\\r\\n'" "'s/\\r\$//'"
printf '1,"a\r\nb"\r\n' | sed 's/\r$//' | xxd | sed 's/^/  /'
printf '\n  The same wrong answer twice: a customer note that said CRLF now says\n'
printf '  LF, and the file still parses, so nothing will ever report it. There\n'
printf '  is no sed or tr or awk that gets this right, because getting it right\n'
printf '  needs a parser that knows which 0a bytes are inside quotes. Fix the\n'
printf '  endings of a quoted CSV in the program that reads it -- section 4 of\n'
printf '  the Python run -- and not in the pipeline in front of it.\n'
printf '\n  dos2unix does the sed job with a safety net (it refuses a binary file\n'
printf '  and keeps the mode bits) and is the right answer at a keyboard -- but\n'
printf '  it ships with neither macOS nor a stock Ubuntu, so it is not used\n'
printf '  here and should not go in a script you expect to run anywhere.\n'

say "5. AND BACK THE OTHER WAY"
show "sed 's/\$/\r/' unix.txt | xxd"
printf "  tr cannot do this direction at all -- tr substitutes and deletes, it\n"
printf "  never inserts. This is the sed to reach for when a Windows consumer\n"
printf "  insists, and it is what unix2dos does.\n"

say "6. A SCRIPT SAVED WITH CRLF"
printf '#!/bin/bash\r\necho hello\r\n' > greet.sh
printf '  the script:  '; cat -vet greet.sh | tr '\n' ' ' | sed 's/ $//'; printf '\n'
printf '  bash greet.sh prints:  %s\n' "$(bash greet.sh | xxd -p)"
printf '\n  68 65 6c 6c 6f is "hello", and then 0d 0a. The CR was never a line\n'
printf '  ending to bash -- it was the last character of the ARGUMENT to echo,\n'
printf '  so the script now prints an invisible carriage return into whatever\n'
printf '  reads it. It ran. It even looks right on screen.\n'
printf '\n  Give it a block and it stops running at all:\n'
printf '#!/bin/bash\r\nif true; then\r\n  echo yes\r\nfi\r\n' > block.sh
set +e
bash block.sh >/dev/null 2>&1
status=$?
set -e
printf '  bash block.sh   exit=%s   (a syntax error, on a script with no\n' "$status"
printf '                            syntax error in it -- "fi" followed by a\n'
printf '                            CR is not the word fi)\n'
printf '\n  And when the kernel runs it directly, the CR joins the interpreter\n'
printf '  path: the shebang asks for "/bin/bash", CR, which does not exist. Both\n'
printf '  the message and the exit status for THAT differ by platform, so\n'
printf '  neither can be recorded here -- "The first two bytes" compares three\n'
printf '  shells side by side and is where that half of the story lives.\n'

say "7. THE FILE THAT IS BOTH"
printf '  %-10s %s\n' "mixed.txt" "$(file -b mixed.txt)"
show "cat -vet mixed.txt"
printf '  One CRLF line and one LF line, which is what every editor produces\n'
printf '  the moment two people with different settings touch one file. file(1)\n'
printf '  names both. Nothing else here will: grep, cut and wc each answer for\n'
printf '  their own line and never mention that the file disagrees with itself.\n'
