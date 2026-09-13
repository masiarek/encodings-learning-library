#!/bin/bash
# Dump the Linux man pages this folder annotates -- the ones macOS does not
# ship -- verbatim, into raw/linux/, from an ubuntu:24.04 container.
#
#   bash 13_Documentation/manual_pages/dump_linux.sh    # needs Docker
#
# A stock ubuntu:24.04 image ships NO man pages: dpkg is told to drop
# /usr/share/man (/etc/dpkg/dpkg.cfg.d/excludes) and /usr/bin/man is a stub
# that prints "This system has been minimized". The Dockerfile below lifts the
# exclusion and (re)installs man-db and the manpages packages; the real binary
# is then /usr/bin/man.REAL, still diverted behind the stub. Each page is
# rendered by that binary at 78 columns into `cat`, then through `col -bx`,
# the same finishing step dump.sh uses on macOS. The locale is pinned to
# C.UTF-8, the one a stock Ubuntu ships, so these are the UTF-8 rendering:
# man-db writes real hyphens, dashes and bullets into the text where dump.sh's
# C locale makes mandoc write ASCII.
set -u
cd "$(dirname "$0")" || exit 1
out=raw/linux
mkdir -p "$out"
img=enc-man:latest
if ! docker image inspect "$img" >/dev/null 2>&1; then
  tmp=$(mktemp -d)
  cat > "$tmp/Dockerfile" <<'DOCKER'
FROM ubuntu:24.04
RUN rm -f /etc/dpkg/dpkg.cfg.d/excludes \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends --reinstall \
      man-db manpages manpages-dev bsdextrautils libc-bin locales \
 && rm -rf /var/lib/apt/lists/*
DOCKER
  docker build -t "$img" "$tmp" || exit 1
fi
# One container run: render every page into a directory, tar it to stdout.
docker run --rm "$img" bash -c '
  set -u
  M=/usr/bin/man.REAL; [ -x "$M" ] || M=/usr/bin/man
  mkdir -p /tmp/out; n=0; missing=0
  while read -r sec name; do
    case "$sec" in ""|"#"*) continue ;; esac
    if ! "$M" -w "$sec" "$name" >/dev/null 2>&1; then
      echo "MISSING  $name($sec)" >&2; missing=$((missing+1)); continue
    fi
    LANG=C.UTF-8 MANWIDTH=78 "$M" -P cat "$sec" "$name" 2>/dev/null | LANG=C.UTF-8 col -bx > "/tmp/out/$name.$sec.txt"
    n=$((n+1))
  done <<LIST
# --- the encoding pages Linux has and macOS does not (section 7)
7 utf-8
7 unicode
7 charsets
7 ascii
7 iso_8859-1
7 iso_8859-2
7 iso_8859-15
7 iso_8859-16
7 cp1251
7 cp1252
7 koi8-r
7 koi8-u
7 armscii-8
# --- locale: the concept, the definition file, the charmap, the compiler
7 locale
5 locale
5 charmap
5 repertoiremap
1 localedef
1 locale
7 environ
# --- iconv, GNU flavour
1 iconv
3 iconv
3 iconv_open
# --- the same API pages, for comparison with the BSD ones
3 mbrtowc
3 wcwidth
3 setlocale
3 nl_langinfo
# --- patterns
7 regex
7 glob
LIST
  {
    echo "Linux dump: $(date +%Y-%m-%d)"
    echo "  $(. /etc/os-release; echo "$PRETTY_NAME") in Docker, image enc-man (built from ubuntu:24.04)"
    echo "  manpages $(dpkg-query -W -f=\${Version} manpages), man-db $(dpkg-query -W -f=\${Version} man-db), glibc $(dpkg-query -W -f=\${Version} libc-bin)"
    echo "  rendered with: LANG=C.UTF-8 MANWIDTH=78 man.REAL -P cat SECTION NAME | col -bx   (man-db, UTF-8 rendering)"
    echo "  pages: $n dumped, $missing missing"
  } > /tmp/out/PROVENANCE-linux.txt
  tar -C /tmp/out -cf - .
' | tar -xf - -C "$out"
mv "$out/PROVENANCE-linux.txt" raw/PROVENANCE-linux.txt
cat raw/PROVENANCE-linux.txt
