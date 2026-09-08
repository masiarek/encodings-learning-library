#!/usr/bin/env bash
# Answer key: four mechanisms, four answers, one file.
#
# `file`'s exact wording differs between the BSD and GNU builds, so this key
# records whether its answer CONTAINS the word that matters, never the sentence
# itself. Same discipline as the rest of the chapter: the verdict is portable,
# the phrasing is not.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"

# A real 1x1 PNG header: the 8-byte signature plus an IHDR chunk, because
# file(1) calls the signature alone 'data' on both platforms.
printf '\211PNG\r\n\032\n\0\0\0\015IHDR\0\0\0\1\0\0\0\1\10\6\0\0\0\037\25\304\211' > report.txt
chmod 644 report.txt
printf '#!/bin/sh\necho hi\n' > data.png     # a shell script, named .png
chmod 755 data.png

for f in report.txt data.png; do
  echo "$f"
  printf '   1. NAME          extension %-6s  (a convention; nothing enforces it)\n' ".${f##*.}"
  printf '   2. CONTENT       first bytes %-14s\n' "$(head -c8 "$f" | xxd -p)"
  said=$(file -b "$f")
  for word in PNG image shell script text ASCII; do
    case $said in *"$word"*) printf '      file(1) says something containing %s\n' "$word";; esac
  done
  printf '   3. PERMISSION    mode %s  -- %s\n' \
    "$(ls -l "$f" | cut -c1-10)" \
    "$([ -x "$f" ] && echo 'the kernel will try to run it' || echo 'not executable')"
  printf '   4. WHAT OPENS IT the desktop asks a MIME database keyed on the NAME,\n'
  printf '                    so it agrees with question 1 and not with 2\n'
  echo
done

echo "THE FOUR QUESTIONS, AND WHY THEY DISAGREE WITHOUT ANY OF THEM BEING WRONG"
echo
echo "   1. What is it CALLED?         the extension. A convention between"
echo "      humans; the filesystem stores a name and has no opinion."
echo "   2. What is IN it?             magic bytes. file(1) reads a few and"
echo "      matches a table -- a guess, and it says so by ranking candidates."
echo "   3. May it be EXECUTED?        a permission bit, which is about"
echo "      authority, not about content. An empty file can carry it."
echo "   4. What OPENS it?             a desktop MIME association, usually"
echo "      resolved from the extension -- so it answers question 1 again."
echo
echo "report.txt is PNG content with a text name: 1 and 4 say text, 2 says PNG."
echo "data.png is a script with an image name and the execute bit: 1 and 4 say"
echo "image, 2 says shell script, 3 says the kernel will try to run it -- and"
echo "the kernel is right, because ./data.png works and none of the other three"
echo "questions were consulted."
echo
echo "So 'what type is this file' has no answer on its own. It has four, from"
echo "four sources, and picking the wrong one is the whole of the security"
echo "advice on the subject: trust the CONTENT for what a thing is, and never"
echo "the name -- while remembering that content is a guess too."
