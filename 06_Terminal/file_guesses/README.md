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

Already demonstrated elsewhere, so this page should link rather than repeat it: the three shapes `file`'s answer takes — evidence from a BOM, inference from valid UTF-8, proof of a negative, and the flat `data` it returns for BOM-less UTF-16 — are a table in [Inspecting a file](../inspecting_a_file/README.md), along with `--mime-encoding` as the portable spelling. What is left for this page is *how* it decides: the magic-number database, where that database ends, and the difference between a signature it knows and a heuristic it is running.

## See also

- [Inspecting a file](../inspecting_a_file/README.md) — what `file` says about the same text in five encodings, and what kind of claim each answer is

- [Byte order and the BOM](../../03_Encodings/byte_order_and_bom/README.md)
- [`iconv`](../iconv/README.md)
