#!/bin/sh
# A ripgrep --pre preprocessor that lifts an ENCODING ceiling rather than a
# format one: it hands rg a UTF-8 rendering of a UTF-32LE file, which is an
# encoding rg's own -E flag has no name for and its BOM sniffer misreads.
#
#     rg --pre <this file> PATTERN .
#
# Same contract as any other preprocessor: rg runs it once per file searched,
# passes the filename as $1, and reads this program's stdout instead of the
# file. Anything that is not matched by the first branch is passed through
# untouched, so every other file searches exactly as it would have.
#
# Dispatching on the NAME is the cheap choice and is what this page's session
# measured. Dispatching on content -- `case $(file -b "$1") in ...` -- is the
# honest one, and is what you want if the names cannot be trusted.
#
# Run with no arguments it explains itself, which is also how CI checks that
# the copy printed on the page is the copy in this file.
case "$1" in
    "")     echo "usage: rg --pre $(basename "$0") PATTERN ." ;;
    *u32*)  exec iconv -f UTF-32LE -t UTF-8 "$1" ;;
    *)      exec cat "$1" ;;
esac
