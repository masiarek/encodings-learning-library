# Interfaces and storage

**Level:** 201 · for anyone starting from zero

> **Stub — an outline, not a lesson.** There is no runnable example behind this page yet, so nothing on it has been through [the check that backs every other claim in this library](../../CONTRIBUTING.md). The bullets below are the questions the finished page has to answer.

**One line:** Every protocol has exactly one place where the encoding is declared, and the whole job is knowing where that place is — because when nobody declares it, somebody guesses.

## What the finished page has to answer

- **HTTP**: `Content-Type: text/html; charset=utf-8`, and what happens when the header and the `<meta charset>` disagree (the header wins, and the page still renders wrongly for the person who only edited the meta tag)
- **JSON**: UTF-8 by [RFC 8259 ↗](https://www.rfc-editor.org/rfc/rfc8259#section-8.1) — no charset parameter exists, so a JSON file in cp1252 is not "JSON in another encoding", it is broken JSON. And `ensure_ascii=False`
- **CSV**: the format with no declaration at all. The BOM as Excel's de-facto marker; `utf-8-sig` to read and `utf-8` to write; `newline=''`; the separator that changes with the Windows regional setting
- **Databases**: MySQL's `utf8` meaning a three-byte subset that cannot store an emoji, versus `utf8mb4` which is real UTF-8 and the default since MySQL 8.0; PostgreSQL's `UTF8` and the `client_encoding` setting; and why a `VARCHAR(50)` counts different things in different engines
- **Filesystems**: bytes on Unix, UTF-16 on Windows, and the historical NFD normalization of HFS+ filenames on macOS that makes a Polish filename compare unequal after a copy
- **SAP**: the Unicode system storing UTF-16 internally, `OPEN DATASET … ENCODING`, and the code-page number belonging to the interface specification rather than the file — full table in [SAP code pages](../../07_Real_Data/sap_code_pages/README.md)
- The through-line: **name the encoding at every boundary you control**, and when you receive from a boundary you do not control, find out which of the above declared it

## The example it will run

A single record — one Polish city name — written and read back across four declarations: a JSON payload, a CSV with and without a BOM, a fixed-width field measured in bytes, and a URL-encoded query string. The point is that four correct-looking pipelines give four different byte counts for the same name.

## See also

- [UTF-8 everywhere](../utf8_everywhere/README.md)
- [07_Real_Data](../../07_Real_Data/README.md) — the six shapes this takes on a real SAP interface
- [BOM in a CSV](../../07_Real_Data/bom_in_a_csv/README.md)
