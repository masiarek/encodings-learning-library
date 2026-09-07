"""The same file, asked three ways, answering three different things.

Python has a separate API for each layer, and picking the wrong one is the
classic bug: os.stat asks the inode, mimetypes asks the FILENAME and never
opens anything, and only a byte-sniffer asks the content.

Run:  python3 file_type_four_questions_py.py
"""

import atexit
import mimetypes
import os
import shutil
import stat
import tempfile

# The first 33 bytes of a 1x1 PNG: 8-byte signature, then the IHDR chunk.
PNG = (b"\x89PNG\r\n\x1a\n"
       b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
       b"\x1f\x15\xc4\x89")

# A miniature magic database: (offset, signature, what it means).
MAGIC = [
    (0, b"\x89PNG\r\n\x1a\n", "image/png"),
    (0, b"\x1f\x8b", "application/gzip"),
    (0, b"%PDF-", "application/pdf"),
    (0, b"#!", "text/x-shellscript"),
]


def sniff(path):
    """Stage two, in miniature: compare bytes, ignore the name."""
    with open(path, "rb") as fh:
        head = fh.read(64)
    if not head:
        return "inode/x-empty"
    for offset, sig, kind in MAGIC:
        if head[offset:offset + len(sig)] == sig:
            return kind
    try:                                  # stage three, in miniature
        head.decode("utf-8")
        return "text/plain"
    except UnicodeDecodeError:
        return "application/octet-stream"


def inode_kind(path):
    """Stage one: four bits of st_mode. lstat, so a symlink stays a symlink."""
    mode = os.lstat(path).st_mode
    for name, test in (("directory", stat.S_ISDIR), ("regular file", stat.S_ISREG),
                       ("symlink", stat.S_ISLNK), ("fifo", stat.S_ISFIFO),
                       ("socket", stat.S_ISSOCK)):
        if test(mode):
            return name
    return "something else"


tmp = tempfile.mkdtemp()
atexit.register(shutil.rmtree, tmp, True)
os.chdir(tmp)

open("liar.txt", "wb").write(PNG)        # PNG bytes, .txt name
open("real.png", "wb").write(b"plain\n")  # ASCII text, .png name
open("empty.png", "wb").close()           # nothing at all, .png name
open("cafe.dat", "wb").write("café\n".encode("utf-8"))
os.mkdir("adir")
os.symlink("liar.txt", "alink")

print("1. THE INODE KNOWS SEVEN THINGS, AND CONTENT IS NOT ONE OF THEM")
print("   os.lstat() reads the directory entry. It never opens the file, so")
print("   it cannot be lied to by the bytes and cannot see them either.")
for name in ("liar.txt", "adir", "alink"):
    mode = os.lstat(name).st_mode
    print("   %-10s type bits = %-9s ->  %s"
          % (name, oct(stat.S_IFMT(mode)), inode_kind(name)))
print("   The whole type lives in S_IFMT. Everything else in st_mode is")
print("   permissions - so with the permissions pinned to 0o644:")
os.chmod("liar.txt", 0o644)
mode = os.lstat("liar.txt").st_mode
print("     st_mode   %s" % oct(mode))
print("     S_IFMT    %-9s the type: regular file" % oct(stat.S_IFMT(mode)))
print("     & 0o7777  %-9s the permissions" % oct(stat.S_IMODE(mode)))
print("   Four bits carry the type. That is the entire vocabulary the")
print("   filesystem layer has for the question, and 'PNG' is not in it.")
print("   (The permission bits are left out of the rows above on purpose:")
print("   a symlink is 0o120755 on macOS and 0o120777 on Linux, so printing")
print("   them would make this page's answer key depend on the machine.)")

print()
print("2. os.stat FOLLOWS A SYMLINK; os.lstat DOES NOT")
print("   alink -> liar.txt.  A symlink is the one type you can only see by")
print("   asking not to follow it:")
print("   os.lstat('alink') -> %s" % inode_kind("alink"))
print("   os.stat('alink')  -> %s"
      % ("regular file" if stat.S_ISREG(os.stat("alink").st_mode) else "?"))
print("   pathlib.Path.is_file() follows too, so it answers True for a")
print("   symlink and tells you nothing about which of the two you have.")

print()
print("3. mimetypes ASKS THE FILENAME AND NOTHING ELSE")
print("   It is a lookup table over the extension. It never opens the file,")
print("   so it is wrong exactly when the name is:")
for name in ("liar.txt", "real.png", "empty.png", "cafe.dat"):
    print("   %-10s mimetypes.guess_type -> %s" % (name, mimetypes.guess_type(name)[0]))
print("   Two of those four are wrong, and one is None because .dat is not in")
print("   the table. None means 'no opinion', never 'not a known type'.")

print()
print("4. ONLY READING THE BYTES ANSWERS THE QUESTION ASKED")
print("   %-10s %-14s %-16s %s" % ("file", "inode", "by name", "by bytes"))
for name in ("liar.txt", "real.png", "empty.png", "cafe.dat", "adir"):
    by_name = mimetypes.guess_type(name)[0] or "-"
    by_bytes = "-" if os.path.isdir(name) else sniff(name)
    print("   %-10s %-14s %-16s %s" % (name, inode_kind(name), by_name, by_bytes))
print("   Three columns, three different questions, and on liar.txt three")
print("   different answers - none of which is wrong. They were asked")
print("   'how is it stored', 'what is it called' and 'what is in it'.")
