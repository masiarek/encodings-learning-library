#!/usr/bin/env bash
# "What type is this file?" has no single answer. file(1) runs THREE test
# classes in a fixed order and stops at the first hit; this script builds a
# file that each stage answers, and shows the earlier stage winning.
#
# Everything here uses --mime-type, which is stable across file(1) versions.
# The English wording (file -b) is NOT: macOS ships file-5.41 and Ubuntu
# ships 5.45, and they word a shell script differently. That comparison is on
# the page, in a dated fence, because no answer key could hold both.
#
# Run:  bash file_type_four_questions_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

# The first 33 bytes of a 1x1 PNG: the 8-byte signature, then the IHDR chunk.
png() { printf '\211PNG\r\n\032\n\000\000\000\015IHDR\000\000\000\001\000\000\000\001\010\006\000\000\000\037\025\304\211' > "$1"; }

png liar.txt                       # PNG bytes wearing a .txt name
png noext                          # PNG bytes with no name to go on
printf 'caf\303\251\n' > utf8.dat  # 'café' in UTF-8: five characters, six bytes
printf 'plain\n'        > real.png # ASCII text wearing a .png name
: > empty.png                      # nothing at all, wearing a .png name
mkdir adir
mkfifo apipe

echo "1. STAGE ONE - THE FILESYSTEM TESTS"
echo "   Before file(1) reads a single byte it calls stat(). If the answer is"
echo "   'this is not a regular file', or 'this is a regular file of length"
echo "   zero', that IS the answer and no other test runs."
for f in adir apipe empty.png; do
  printf '   %-10s %s\n' "$f" "$(file --mime-type -b "$f")"
done
echo "   Note empty.png. It is named .png, and a magic test would have to read"
echo "   bytes to disagree - but there are no bytes, and stage one already"
echo "   answered. inode/x-empty is a claim about the INODE, not the content."

echo
echo "2. STAGE TWO - THE MAGIC TESTS"
echo "   Only now does file(1) open the file and compare bytes against its"
echo "   compiled database. The filename is not an input to this stage."
for f in liar.txt noext; do
  printf '   %-10s %s\n' "$f" "$(file --mime-type -b "$f")"
done
echo "   Same 33 bytes, two names, one answer. And the reverse case:"
printf '   %-10s %s\n' real.png "$(file --mime-type -b real.png)"
echo "   real.png is named .png and file(1) does not care, because no rule in"
echo "   the database matches the bytes 'p l a i n'."

echo
echo "3. STAGE THREE - THE LANGUAGE AND ENCODING TESTS"
echo "   Nothing matched. The last question is 'could this be text?', which is"
echo "   answered by validating byte sequences, not by looking anything up."
printf '   %-10s type=%s encoding=%s\n' utf8.dat \
  "$(file --mime-type -b utf8.dat)" "$(file --mime-encoding -b utf8.dat)"
printf '   %-10s type=%s encoding=%s\n' real.png \
  "$(file --mime-type -b real.png)" "$(file --mime-encoding -b real.png)"
echo "   'café' has no signature. UTF-8 has no signature. utf-8 here is an"
echo "   INFERENCE - those six bytes are a valid UTF-8 sequence, so file(1)"
echo "   says so. Stage three is the only stage that guesses."

echo
echo "4. THE STAGES ARE ORDERED, AND THE FIRST HIT WINS"
echo "   Give the PNG bytes a length of zero and watch stage one take the"
echo "   answer away from stage two:"
png shrink.png
printf '   %-22s %s\n' "33 bytes of PNG" "$(file --mime-type -b shrink.png)"
: > shrink.png
printf '   %-22s %s\n' "same name, 0 bytes" "$(file --mime-type -b shrink.png)"
echo "   Same path, same name, same database. The only thing that changed is"
echo "   which stage got to answer first."

echo
echo "5. THE SHELL NEVER ASKS ANY OF THIS"
echo "   [ -f ] and friends are stat() and nothing else. They read no bytes,"
echo "   so they cannot be fooled by content and cannot see it either."
for f in liar.txt adir apipe empty.png; do
  t=""
  [ -f "$f" ] && t="$t -f"
  [ -d "$f" ] && t="$t -d"
  [ -p "$f" ] && t="$t -p"
  [ -s "$f" ] && t="$t -s"
  printf '   %-10s%s\n' "$f" "${t:-  (none of -f -d -p -s)}"
done
echo "   liar.txt is -f and -s: a regular file, non-empty. That is the whole"
echo "   of what the shell knows, and it is true of a PNG, a novel and a core"
echo "   dump alike."
