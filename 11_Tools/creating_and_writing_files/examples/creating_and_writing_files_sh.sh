#!/usr/bin/env bash
# The commands that make a file, and the ways they are not the same command.
#
# Everything here has to print the same thing on BSD and on GNU, because the
# answer key is checked on both. Three consequences worth knowing before you
# read it:
#
#   * No raw `ls -l`, `wc -c` or `stat` output. The two `wc`s pad their column
#     differently, `stat` takes -f on BSD and -c on GNU, and an inode number is
#     not the same twice in a row anyway. Every one of those is asked through a
#     helper that prints a VERDICT — same, changed, 0 — never the raw field.
#   * Only stdout is recorded. `dd` writes its three-line report to stderr and
#     the two versions word it differently; the shell's noclobber refusal goes
#     there too. Both are sent to /dev/null and read as an exit status instead.
#   * `sh -c 'echo -n hi'` is the one thing on this subject that CANNOT be
#     recorded: /bin/sh is bash on a Mac and dash on Ubuntu, and they disagree.
#     Section 4 reproduces the Mac's answer portably instead — see the comment
#     there — and the page quotes the real per-platform run in a dated fence.
#
# Run:  bash creating_and_writing_files_sh.sh
set -eu

show() { printf '$ %s\n' "$1"; eval "$1"; }
run()  { printf '$ %s\n' "$1"; local st=0; eval "$1" >/dev/null 2>&1 || st=$?; printf '   exit=%d\n' "$st"; }

# stat is spelled two ways, and NOT as a fallback pair: -f is the format string
# on BSD and "show the FILESYSTEM, not the file" on GNU, so `stat -f '%i' x ||
# stat -c '%i' x` succeeds on both platforms and is right on one of them. Probe
# once for which stat this is, then never guess again.
if stat -c '%i' . >/dev/null 2>&1; then STATFMT=-c; INO='%i'; MOD='%a'
else                                   STATFMT=-f; INO='%i'; MOD='%Lp'; fi
inode() { stat "$STATFMT" "$INO" "$1"; }
mode()  { stat "$STATFMT" "$MOD" "$1"; }
size()  { wc -c < "$1" | tr -d ' '; }
hex()   { xxd -p < "$1" | tr -d '\n'; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

echo "1. SEVEN WAYS TO MAKE AN EMPTY FILE, AND SEVEN ZEROS"
touch                        a.txt
: >                          b.txt
truncate -s 0                c.txt
cp /dev/null                 d.txt
install -m 644 /dev/null     e.txt
dd if=/dev/null of=f.txt     2>/dev/null
printf ''                  > g.txt
for f in a b c d e f g; do printf '   %s.txt  %s bytes\n' "$f" "$(size $f.txt)"; done
echo "   Seven commands, seven empty files, and on a fresh name that really is"
echo "   all there is to say. The list is worth having because the file you"
echo "   want to empty usually already exists — and that is a different"
echo "   question, which is section 2."

echo
echo "2. THE SAME SEVEN, POINTED AT A FILE THAT ALREADY HAS SOMETHING IN IT"
printf '   %-31s %-9s %-11s %s\n' "command" "t.txt" "its 2nd name" "mode (was 600)"
for cmd in "touch t.txt" \
           ": > t.txt" \
           "truncate -s 0 t.txt" \
           "cp /dev/null t.txt" \
           "install -m 644 /dev/null t.txt" \
           "dd if=/dev/null of=t.txt" \
           "printf '' > t.txt"; do
  rm -f t.txt link.txt
  printf 'old content\n' > t.txt
  chmod 600 t.txt
  ln t.txt link.txt              # a second NAME for the same file
  eval "$cmd" >/dev/null 2>&1
  [ "$(size t.txt)"    = 0 ] && kept=emptied  || kept="kept"
  [ "$(size link.txt)" = 0 ] && also=emptied  || also="still 12b"
  printf '   %-31s %-9s %-11s %s\n' "$cmd" "$kept" "$also" "$(mode t.txt)"
done
echo "   Row 1 is the one everybody knows: touch does not empty anything, it"
echo "   sets timestamps, and creating the file is what it does when there is"
echo "   nothing to timestamp. Rows 2, 3, 4, 6 and 7 all TRUNCATE the file that"
echo "   is already there: the mode survives, and so does the second name,"
echo "   because what changed is the file both names point at. Those five are"
echo "   interchangeable and choosing between them is a matter of taste."
echo "   Row 5 is not in that family at all. install REPLACES: it unlinks the"
echo "   name, puts a new file there, and -m decides the mode rather than"
echo "   preserving it. The old file is still twelve bytes and still reachable"
echo "   through the other name — and through any process that had it open."
echo "   That is install doing its job, and it is only a surprise when it is"
echo "   being used as a seventh way to type ': >'."

echo
echo "3. THE COLUMN THAT LOOKS LIKE IT WOULD ANSWER THIS, AND DOES NOT"
rm -f t.txt link.txt
printf 'old content\n' > t.txt
ln t.txt link.txt
install -m 644 /dev/null t.txt >/dev/null 2>&1
printf '   after install, link.txt still holds %s bytes: not the same file\n' "$(size link.txt)"
printf '   and the inode number of t.txt? that one is not printed here.\n'
echo "   It is not printed because it is not stable enough to be an answer key,"
echo "   and that is the lesson rather than an inconvenience. Measured on"
echo "   2026-09-07: this same install came back with a DIFFERENT number six"
echo "   times out of six on APFS and on overlayfs when run in a clean"
echo "   directory, and with the SAME number inside this script, where the"
echo "   earlier sections had already freed one for it to reuse. An inode"
echo "   number is unique among the files that exist right now, not across"
echo "   time: unlink a file and the number goes back in the pool, and the"
echo "   very next create may be handed it. So a number that did not change"
echo "   is not evidence that the file survived, and a number that did change"
echo "   is not evidence that anything was lost. The second name is evidence."
echo "   When the question is whether this is still the same file, ask"
echo "   something that holds it open — another link, or a descriptor — and"
echo "   not a number that is only promised to be unique today."

echo
echo "4. WHAT EACH WAY OF WRITING A LINE ACTUALLY PUTS IN THE FILE"
echo 'text'                        > w1.txt
printf 'text'                      > w2.txt
printf 'line 1\nline 2\n'          > w3.txt
cat <<< 'text'                     > w4.txt
echo 'text' | tee w5.txt         > /dev/null
# Reproducing a Mac's /bin/sh, which is bash in posix mode with xpg_echo on.
# Written out longhand so that this line means the same thing under bash 3.2
# and bash 5: `sh -c` and `bash --posix -c` would not.
bash -c 'shopt -s xpg_echo; set -o posix; echo -n text' > w6.txt
bash -c 'echo -n text'             > w7.txt
printf '   %-42s %s\n' "echo 'text' > f"              "$(hex w1.txt)"
printf '   %-42s %s\n' "printf 'text' > f"            "$(hex w2.txt)"
printf '   %-42s %s\n' "printf 'line 1\\nline 2\\n' > f" "$(hex w3.txt)"
printf '   %-42s %s\n' "cat <<< 'text' > f"           "$(hex w4.txt)"
printf '   %-42s %s\n' "echo 'text' | tee f"          "$(hex w5.txt)"
printf '   %-42s %s\n' "echo -n text   (a POSIX echo)" "$(hex w6.txt)"
printf '   %-42s %s\n' "echo -n text   (bash builtin)" "$(hex w7.txt)"
echo "   74 65 78 74 is text. Four of the seven append an 0a you did not type:"
echo "   echo, the here-string, and tee-behind-echo all end the line for you,"
echo "   and that is usually right, because a text file's last byte is normally"
echo "   a newline. printf writes what it is given and nothing else."
echo "   The last two rows are the same six characters twice. A POSIX echo has"
echo "   no -n option, so it prints the flag as text AND ends the line anyway:"
echo "   2d 6e 20 is '-n ', and the file is six bytes longer than the file you"
echo "   asked for. bash's builtin, and zsh's, and dash's, all honour -n. This"
echo "   is not a Linux-versus-Mac split; it is a which-shell split, and the"
echo "   shell in question is whatever /bin/sh happens to be where the script"
echo "   finally runs. printf is the way to write bytes without a newline."

echo
echo "5. THE HEREDOC DELIMITER IS A QUOTING DECISION"
NAME=Adam
cat << EOF > h1.txt
hello $NAME, and $(echo a command)
EOF
cat << 'EOF' > h2.txt
hello $NAME, and $(echo a command)
EOF
printf '   << EOF    -> %s\n' "$(cat h1.txt)"
printf "   << 'EOF'  -> %s\n" "$(cat h2.txt)"
echo "   Same three lines of typing, and the quotes around the word EOF are the"
echo "   whole difference. Unquoted, the body is a double-quoted string: \$NAME"
echo "   expands and \$( ) runs. Quoted, the body is literal. Neither is the"
echo "   default you should assume — when the heredoc is a config file, a"
echo "   Dockerfile or somebody else's script, quote the delimiter, and when it"
echo "   is a template you are filling in, do not."

echo
echo "6. THE REDIRECT THAT REFUSES, AND THE ONE THAT CANNOT"
run 'bash -c "set -o noclobber; echo one > n.txt; echo two > n.txt"'
run 'bash -c "set -o noclobber; echo one > n2.txt; : > n2.txt"'
run 'bash -c "set -o noclobber; echo one > n3.txt; echo two >| n3.txt"'
run 'bash -c "set -o noclobber; echo one > n4.txt; truncate -s 0 n4.txt"'
echo "   noclobber makes > refuse to overwrite an existing file, and ': >' is"
echo "   not an exception to it: the ':' is a command that runs no risk, but"
echo "   the redirection beside it is the same redirection. The override is"
echo "   '>|'. And the last row is the reason to know which of these idioms is"
echo "   a shell feature and which is a program — truncate is a program, so"
echo "   noclobber has no opinion about it and the file is emptied regardless."

echo
echo "7. AN EMPTY FILE, AND A FILE FULL OF NOTHING"
truncate -s 0 z.txt
z0=$(hex z.txt); printf '   truncate -s 0  -> %s bytes, hex: %s\n' "$(size z.txt)" "${z0:-(nothing)}"
truncate -s 5 z.txt
printf '   truncate -s 5  -> %s bytes, hex: %s\n' "$(size z.txt)" "$(hex z.txt)"
echo "   truncate sets a length, and growing is as much a length change as"
echo "   shrinking. The five bytes it invents are NUL, which makes this the"
echo "   fastest way to turn a text file into one that diff will call binary"
echo "   and that most tools will stop reading at. An empty file holds no"
echo "   bytes; this one holds five, and prints as nothing either way."
