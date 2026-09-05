# `file` guesses

**Level:** 101 · for anyone with a terminal

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** `file` reports what an encoding *looks like*, not what it is — `UTF-8 Unicode text` is an inference from the bytes it happened to see, and a pure-ASCII file is every encoding at once.

## What the finished page has to answer

- `file -i` / `file --mime-encoding`: the machine-readable form, and the four answers you will actually see (`us-ascii`, `utf-8`, `iso-8859-1`, `binary`)
- Why ASCII is undecidable: a file of `A`s is valid Latin-1, valid UTF-8, valid CP1252 and valid Latin-2 with the same meaning under all of them
- How it decides UTF-8: it validates the byte sequences; how it decides Latin-1: it gave up on UTF-8 and saw high bytes
- The BOM shortcut, and the one case where `file` is *sure*
- Why this page's example cannot be recorded verbatim: `file`'s wording changes between versions, so the example asks `--mime-encoding` only

## The example it will run

Shell: four small files made with `printf`, `file --mime-encoding` on each.

## See also

- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md)
- [`iconv`](../iconv/README.md)
