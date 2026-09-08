# PRECIS: stringprep, after stringprep

**Level:** 301 · for anyone who stores a username or a password

**One line:** stringprep listed what was *forbidden* and froze the table to stay deterministic; PRECIS derives what is *allowed* from live Unicode properties, so it never needs reissuing — and hands you back the version problem the freeze was there to solve.

**Read [Preparing a string](../preparing_a_string/README.md) first.** That page is the four steps, the frozen 2002 table, and the argument that preparation is a policy question rather than an encoding one. This one is what replaced it, and it only makes sense against that background.

```python
# the same string, through the two profiles of one RFC
username_case_mapped('Straße')   # 'strasse'   <- folded hard: same user as STRASSE
opaque_string('Straße')          # 'Straße'    <- a password: touched as little as possible
```

## The inversion

RFC 3454 is a list. Nine tables of prohibited characters, two mapping tables, all of it pinned to Unicode 3.2, and the pin is what makes it deterministic — the reason [Preparing a string](../preparing_a_string/README.md) can print answers that are identical on every machine.

A list of the forbidden has one structural problem: **Unicode keeps growing, and the list does not.** Every September brings characters nobody legislated about, and the only fix is to reissue the document. RFC 3454 was obsoleted by 7564, which was obsoleted by [8264 ↗](https://www.rfc-editor.org/rfc/rfc8264), inside thirteen years.

[PRECIS ↗](https://www.rfc-editor.org/rfc/rfc8264) — *Preparation, Enforcement, and Comparison of Internationalized Strings* — turns the question round. Instead of enumerating what is forbidden, it gives an **algorithm that derives what is allowed** from the Unicode properties a character already has. A new letter is admitted the day it is assigned, because it is a letter, and nobody has to publish anything.

| | stringprep, 2002 | PRECIS, 2015 |
|---|---|---|
| what the document holds | tables of the **forbidden** | a derivation of the **allowed** |
| the Unicode table | **frozen** at 3.2 | **live**, whichever your build has |
| a character invented last year | permanently refused | admitted if its properties qualify |
| two implementations | agree, always | may disagree — see below |

## Two classes, because a username and a password are not the same kind of string

PRECIS's first move is to split strings by **what they are for**, not by how strict you feel:

- **IdentifierClass** — letters and digits, and very little else. **No spaces.** For strings that get *compared*: usernames, nicknames, resource names.
- **FreeformClass** — letters, digits, spaces, punctuation, symbols, emoji. For strings a person *composes*: passwords, display names, free text.

On top of a class sits a **profile**, which fixes five rules in a normative order — width mapping, additional mapping, case mapping, normalization, directionality. [RFC 8265 ↗](https://www.rfc-editor.org/rfc/rfc8265) defines the two that matter here, and comparing their five slots is the fastest way to see what a password *is*:

| rule | `UsernameCaseMapped` | `OpaqueString` |
|---|---|---|
| 1 width mapping | fullwidth → plain | **none** |
| 2 additional mapping | none | **every non-ASCII space → `U+0020`** |
| 3 case mapping | **casefold** | **none** |
| 4 normalization | NFC | NFC |
| 5 directionality | the Bidi Rule | none |
| the class | IdentifierClass | FreeformClass |

## Why passwords get a different profile

Every difference in that column is a decision, and each one is defensible in one direction only.

**No case folding.** Folding a password shrinks the keyspace, for free, in the attacker's favour. `PAßWORT` and `paßwort` must stay two passwords. Folding a *username* is the opposite call and just as firmly right: two people must not be able to register names no human can tell apart.

**No width mapping.** The username profile folds a fullwidth `ａ` to `a`; the password profile keeps every code point the user typed. Same reasoning — the username is being made comparable, the password is being preserved.

**Spaces allowed, and then mapped.** FreeformClass admits spaces so that a passphrase can be a password. But *which* space? A phone keyboard, a PDF copy-paste or a word processor can hand you `U+00A0` where the user believes they typed a space, so the Additional Mapping Rule folds every non-ASCII space to `U+0020` — which means a password set on the device that inserted the odd space still works tomorrow from one that does not.

**NFC on both, and this is the rule with no free option.** [Passwords are not text](../../12_Adversarial/README.md) in most respects, but they are text in this one: `café` typed composed (`U+0063 U+0061 U+0066 U+00E9`) and the same word typed decomposed (`U+0063 U+0061 U+0066 U+0065 U+0301`, an `e` followed by a combining acute) are the same password to the person typing it — and identical on screen, which is why only a program can tell them apart. Normalize and both spellings log in. Don't, and one of them silently never works — on a Mac, which hands applications decomposed filenames and sometimes decomposed input, that is a support ticket nobody can reproduce.

## In Python

There is no PRECIS in the standard library. `stringprep` is there — the *obsolete* framework, importable today with no deprecation warning — and its successor is not. So the program below implements the two profiles from the RFC, in about forty lines, which is roughly the point: PRECIS is small when you already have `unicodedata`.

<!-- output:precis_after_stringprep_py -->
*Verified output of [`precis_after_stringprep_py.py`](examples/precis_after_stringprep_py.py) — regenerated by `tools/run_examples.py`, never hand-typed.*

```text
1. THE INVERSION
------------------------------------------------------------------------
   stringprep, 2002:  here are the tables of what is FORBIDDEN
   PRECIS,     2015:  here is how to DERIVE what is allowed

   The consequence is a maintenance one, and it is the whole reason
   the framework was replaced. A list of the forbidden has to be
   reissued every time Unicode grows; a derivation does not. RFC 3454
   was obsoleted by 7564, obsoleted by 8264, in thirteen years.

   PRECIS defines two string classes, and the difference is not
   severity -- it is what the string is FOR:

     IdentifierClass  letters and digits, and almost nothing else.
                      NO spaces. For things that get compared.
     FreeformClass    letters, digits, spaces, punctuation, symbols,
                      emoji. For things a person composes.

2. UsernameCaseMapped -- FOLD IT HARD
------------------------------------------------------------------------
   Five rules, and RFC 8264 fixes the order:
     1 width mapping   2 additional mapping   3 case mapping
     4 normalization   5 directionality

   input                prepared         code points
   'Straße'             'strasse'        0073 0074 0072 0061 0073 0073 0065
   'STRASSE'            'strasse'        0073 0074 0072 0061 0073 0073 0065
   'ａdmin'              'admin'          0061 0064 006D 0069 006E
   'ADMIN'              'admin'          0061 0064 006D 0069 006E
   'café'               'café'           0063 0061 0066 00E9
   'café'              'café'           0063 0061 0066 00E9
   'Ada Lovelace'       error: IdentifierClass: U+0020 is Zs
   '🔑🔑🔑'                error: IdentifierClass: U+1F511 is So

   Rows 1 and 2 land on the same prepared string, because casefold
   turns sharp s into two esses. So `Straße` and `STRASSE` are ONE
   username, and the second person to arrive is told the name is
   taken. RFC 8265 knows this and accepts it: two names nobody can
   tell apart must not both be registrable.

   Rows 5 and 6 are the same word typed two ways -- one composed,
   one with a combining acute. NFC reconciles them, which is rule 4
   doing the only job it has.

   Rows 7 and 8 are the CLASS, not the rules. A space is not a
   letter or a digit and neither is a key emoji, so IdentifierClass
   refuses both -- and a profile returns a string or an error, never
   both. Note that nothing was silently dropped: PRECIS does not
   sanitise a username, it declines to have one.

3. OpaqueString -- TOUCH IT AS LITTLE AS POSSIBLE
------------------------------------------------------------------------
   input                      prepared                   code points
   'paßwort'                  'paßwort'                  0070 0061 00DF 0077 006F 0072 0074
   'PAßWORT'                  'PAßWORT'                  0050 0041 00DF 0057 004F 0052 0054
   'correct horse battery staple' 'correct horse battery staple' (28 code points)
   'my\xa0password'           'my password'              006D 0079 0020 0070 0061 0073 0073 0077 006F 0072 0064
   'café'                    'café'                     0063 0061 0066 00E9
   'ａdmin'                    'ａdmin'                    FF41 0064 006D 0069 006E
   '🔑🔑🔑'                      '🔑🔑🔑'                      1F511 1F511 1F511
   'pass\u200bword'           error: FreeformClass: U+200B is Cf

   Four differences from the profile above, and every one of them is
   a decision about what a password IS:

     no case mapping   rows 1 and 2 stay two different passwords.
                       Folding case would shrink the keyspace, and
                       hand an attacker collisions for free.
     spaces allowed    row 3 is a passphrase. FreeformClass exists
                       so that four words can be a password.
     spaces MAPPED     row 4 was typed with a NO-BREAK SPACE, and
                       comes out with an ordinary one -- so a user
                       whose keyboard or phone inserted U+00A0 can
                       still log in tomorrow from a machine that
                       inserts U+0020.
     no width mapping  row 6's fullwidth `a` is NOT folded to `a`.
                       The username profile folds it; the password
                       profile keeps every bit the user typed.

   Rows 7 and 8 are the class doing its job in both directions. A
   password may be three key emoji, because FreeformClass admits
   symbols -- and may NOT contain a ZERO WIDTH SPACE, because that
   is a format character, and a password with an invisible character
   in it is one the user can never retype. Section 5 is about how
   close those two verdicts are to each other.

   Row 5 shows the one rule both profiles share, and it is the one
   with no free option. NFC is applied to passwords too -- because
   the alternative is a password that works on the keyboard it was
   set on and silently never works anywhere else.

4. THE SAME STRING, THROUGH BOTH
------------------------------------------------------------------------
   input                            as a username            as a password
   'Straße'                         'strasse'                'Straße'
   'ａdmin'                          'admin'                  'ａdmin'
   'correct horse battery staple'   error: IdentifierClass   'correct horse battery staple'
   'café'                          'café'                   'café'
   '🔑🔑🔑'                            error: IdentifierClass   '🔑🔑🔑'

   One framework, one document, two answers per row. `Preparing a
   string` made the case that preparation is a policy question; this
   is that argument with the policies written out side by side.

5. WHAT PRECIS TOOK BACK WHEN IT UNPINNED THE TABLE
------------------------------------------------------------------------
   stringprep froze Unicode 3.2 so a registered name could never
   change meaning. The cost was that it can never accept a character
   invented after 2002. PRECIS derives from the LIVE table instead,
   so it grows -- and inherits the problem the freeze was there to
   solve. A property PRECIS reads can move.

   Here is one that did, and Python ships both tables to prove it:

   U+200B ZERO WIDTH SPACE
     general category in the frozen 2002 table:  'Zs'

   `Zs` is the category PRECIS's Additional Mapping Rule means by
   `space`. Read under a 2002 table, a ZERO WIDTH SPACE in a password
   IS a space and gets MAPPED to U+0020. It has since been
   reclassified as a format character, so a modern table puts it in
   `Cf` and PRECIS DISALLOWS it instead -- which is the verdict the
   last row of section 3 printed.

   This program can prove the two endpoints and deliberately does not
   name the version in between: the frozen table is shipped and so is
   printable, and the release that moved the character is a fact this
   program has no way to check.

   Same character, same rule, same RFC: mapped on one machine and
   refused on another, decided by nothing but which Unicode the
   implementation was built against.

   This program does not print what YOUR table says, because that
   would be a fact about your machine rather than about text -- and
   the frozen answer above is printable precisely because it is
   frozen. Run it yourself:

     python3 -c "import unicodedata as u; print(u.category('\u200b'))"

   That is the honest shape of the trade, and neither side of it is
   a mistake. stringprep bought determinism with a permanent freeze:
   a name registered in 2003 means the same thing forever, and no
   character invented since may ever be registered. PRECIS bought
   growth with a version number -- your users can have the alphabet
   they actually write in, and `is this string allowed` is now a
   question about which Unicode your server was built against.
```
<!-- /output -->

## The version problem, handed back

Section 5 is the one to sit with, and it is why this page exists rather than being a paragraph on the stringprep page.

PRECIS reads Unicode properties **live**, so a property it depends on can move — and one it depends on has moved. `U+200B ZERO WIDTH SPACE` is general category `Zs` in the frozen 2002 table Python still ships, and `Cf` in a modern one. `Zs` is exactly what PRECIS's Additional Mapping Rule means by *space*. So:

- read against a 2002 table, a ZERO WIDTH SPACE in a password **is a space** and gets mapped to `U+0020`;
- read against a modern table, it is a format character and is **disallowed** outright.

Same character, same rule, same RFC, and the two implementations differ by nothing except which Unicode they were built against. The program prints the frozen half — that one is shipped, so it is printable — and deliberately declines to print your machine's half, for the reason [The table has a version](../the_table_has_a_version/README.md) sets out.

Neither framework made a mistake here. **stringprep bought determinism with a permanent freeze**: a name registered in 2003 means the same thing forever, and no character invented since may ever be registered — so somebody who writes their language in a code point assigned in 2010 cannot have a name. **PRECIS bought growth with a version number**: your users get the alphabet they actually write in, and *is this string allowed* becomes a question about your server's build.

That loop is the whole history of this subject in two documents, and it is the same shape as the trade [Preparing a string](../preparing_a_string/README.md) found inside `in_table_a1`. There is no third option where the table is both frozen and current.

## What this implementation is not

Forty lines is not an RFC. Named, so nobody mistakes one for the other:

- **The derivation is transcribed, not computed.** Real PRECIS classifies a code point by an ordered cascade of about a dozen categories — `Exceptions`, `BackwardCompatible`, `Unassigned`, `ASCII7`, `JoinControl`, `OldHangulJamo`, `PrecisIgnorableProperties`, `Controls`, `HasCompat`, `LetterDigits`, `OtherLetterDigits`, and the rest — where the **order is normative** and first match wins. The program here transcribes the general categories of exactly the characters this page uses, and raises rather than guessing on anything else. That is a deliberate limitation, taken so that nothing on the page is a fact about the machine that ran it; it is also, precisely, the frozen-table move PRECIS was designed to avoid.
- **The Bidi Rule is not implemented.** `UsernameCaseMapped` requires [RFC 5893 ↗](https://www.rfc-editor.org/rfc/rfc5893)'s directionality check, which is the same shape as the bidi step on the stringprep page and needs the `Bidi_Class` of every character.
- **`Nickname` is not here.** [RFC 8266 ↗](https://www.rfc-editor.org/rfc/rfc8266) is the third profile — for display names — and it does the interesting thing of preparing *for comparison* while storing what the user typed. That is the *fold to compare, store what they typed* rule, written into a standard.
- **The libraries.** [`precis-i18n` ↗](https://pypi.org/project/precis-i18n/) in Python and `precis-rs`/`stringprep` in Rust ship the full derivation and the tables. As with [line breaking](../where_a_line_may_break/README.md), what the library adds is **data**, not cleverness.

## If you are coming from Python or ABAP

**Python.** The standard library has the obsolete framework and not its replacement: `import stringprep` works, `'…'.encode('idna')` is IDNA2003, and there is no PRECIS anywhere. If you compare usernames, `unicodedata.normalize('NFC', s.casefold())` is most of `UsernameCaseMapped` and is a large improvement on `s.lower()`; if you handle passwords, the one line worth adding today is `unicodedata.normalize('NFC', password)` **before** hashing, and never `casefold()`. For anything you would defend in a review, use `precis-i18n`.

**ABAP.** *(Not machine-checked — CI cannot run ABAP.)* There is no stringprep and no PRECIS in ABAP, so a username comparison is whatever the code does before the `=`. Two things carry over intact. First, `TRANSLATE … TO UPPER CASE` is not case folding — see [Case is not a per-character operation](../case_is_not_per_character/README.md) — and it is not a substitute for a profile; upper-casing both sides of a comparison leaves two spellings of an accented name as two different keys, because nothing normalized them. Second, and more practical: if a system stores passwords or password-shaped secrets entered from more than one client, normalize to NFC at exactly one place on the way in, and write down where that place is. Doing it in two places with different rules is how a credential becomes unverifiable, and doing it in none is how a Mac user's password stops working on Windows. The house rule from the stringprep page applies unchanged — the preparation rule belongs in one method every path calls, written down like a profile.

## Try it

1. Take your own login system and answer the five rules for it: does it width-map, case-fold, normalize, check directionality, and which class does it enforce? Most systems answer "lowercase, and no" to all five.
2. Set a password containing a `U+00A0` (copy one out of a PDF), then try to log in typing an ordinary space. Whether that works tells you whether anything in your stack implements rule 2.
3. Register `Straße` as a username where you can, then try `STRASSE`. If both succeed you have two accounts nobody can tell apart; if the second is refused, something implemented `UsernameCaseMapped` and you have just found where.
4. `python3 -c "import unicodedata as u; print(u.category('​'), u.ucd_3_2_0.category('​'))"` — the two answers your interpreter holds at once.
5. Find where your code normalizes a password, and check it happens on the same side of the hash on every path — the web form, the mobile client, the password-reset link.

## See also

- [Preparing a string](../preparing_a_string/README.md) — the framework this one replaced; read it first
- [The table has a version](../the_table_has_a_version/README.md) — why a live property lookup is a fact about your machine
- [Case is not a per-character operation](../case_is_not_per_character/README.md) — what rule 3 is actually doing, and why `upper()` is not it
- [Normalization](../../04_Python/normalization/README.md) — rule 4 on its own
- [Confusables and scripts](../confusables_and_scripts/README.md) — the attack no profile on this page prevents
- [Where a line may break](../where_a_line_may_break/README.md) — the other page here where what a library adds is a table
- [RFC 8264 ↗](https://www.rfc-editor.org/rfc/rfc8264) — the framework, and the string classes
- [RFC 8265 ↗](https://www.rfc-editor.org/rfc/rfc8265) — usernames and passwords: `UsernameCaseMapped` and `OpaqueString`
- [RFC 8266 ↗](https://www.rfc-editor.org/rfc/rfc8266) — nicknames, the third profile
- [`precis-i18n` ↗](https://pypi.org/project/precis-i18n/) — the full derivation, with the tables
