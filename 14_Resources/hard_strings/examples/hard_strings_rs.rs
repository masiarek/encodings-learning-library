//! The same corpus, in a standard library that declines to guess.
//!
//! Python answers every question this corpus asks, so the Python page reads as
//! "here are the functions". Rust's std answers some of them and has no
//! opinion about the rest, which makes it the better place to see WHICH half
//! is a language's job and which half is a policy the program has to choose.
//!
//! Sections 2 and 5 are deliberately the same data as the Python example's --
//! the same sixteen pairs in the same order, and the same fourteen invisible
//! characters -- so the two blocks can be read against each other. The rest is
//! what only this language can say: the type of a case mapping, the one string
//! Rust cannot hold at all, and where std stops.
//!
//! Build:  rustc --edition 2024 hard_strings_rs.rs && ./hard_strings_rs

fn bar() {
    println!("{}", "-".repeat(72));
}

/// A string as its code points -- the only unambiguous picture of it.
fn cps(s: &str) -> String {
    s.chars()
        .map(|c| format!("{:04X}", c as u32))
        .collect::<Vec<_>>()
        .join(" ")
}

fn mark(flag: bool) -> &'static str {
    if flag { "=" } else { "-" }
}

/// A Rust string literal in which every non-ASCII character is an escape.
///
/// `{:?}` will not do here: it leaves a printable character as a glyph, and a
/// glyph is exactly what a paste through an editor or a clipboard is allowed to
/// renormalize. `\u{...}` survives that trip; an accent does not.
fn rust_literal(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' | '\\' => {
                out.push('\\');
                out.push(c);
            }
            c if c.is_ascii_graphic() || c == ' ' => out.push(c),
            c => out.push_str(&format!("\\u{{{:x}}}", c as u32)),
        }
    }
    out.push('"');
    out
}

fn main() {
    // ------------------------------------------------------------------ 1
    println!("1. == IS BYTES, AND THE TYPE SAYS SO");
    bar();
    let spellings = [
        ("A", "r\u{e9}sum\u{e9}"),
        ("B", "r\u{e9}sume\u{301}"),
        ("C", "re\u{301}sum\u{e9}"),
        ("D", "re\u{301}sume\u{301}"),
    ];
    println!("      {:3} {:>5} {:>5}   code points", "", "chars", "bytes");
    for (label, s) in spellings {
        println!(
            "      {:3} {:5} {:5}   {}",
            label,
            s.chars().count(),
            s.len(),
            cps(s)
        );
    }
    println!();
    let mut distinct: Vec<&str> = spellings.iter().map(|(_, s)| *s).collect();
    distinct.sort();
    distinct.dedup();
    println!("      distinct values   {}", distinct.len());
    println!();
    println!("   str::len() is the BYTE count and has never pretended otherwise,");
    println!("   so the number Python makes you ask for is the one Rust gives you");
    println!("   by default. Neither language merges the four.");
    println!();

    // ------------------------------------------------------------------ 2
    println!("2. THE SAME SIXTEEN PAIRS, AND EVERYTHING std CAN DO TO THEM");
    bar();
    let pairs: [(&str, &str, &str); 16] = [
        ("caf\u{e9}", "cafe\u{301}", "composed against decomposed"),
        ("\u{c5}", "\u{212b}", "ANGSTROM SIGN against A WITH RING"),
        ("\u{3a9}", "\u{2126}", "OHM SIGN against GREEK CAPITAL OMEGA"),
        ("q\u{307}\u{323}", "q\u{323}\u{307}", "two marks, in two orders"),
        ("\u{fb01}le", "file", "the fi ligature"),
        ("\u{bd}", "1\u{2044}2", "a vulgar fraction"),
        ("10\u{b2}", "102", "a superscript two"),
        ("\u{ff21}\u{ff22}", "AB", "fullwidth forms"),
        ("\u{2168}", "IX", "a Roman numeral"),
        ("stra\u{df}e", "STRASSE", "the German sharp s"),
        ("\u{3a3}", "\u{3c2}", "Greek final sigma"),
        ("\u{212a}", "k", "KELVIN SIGN against the letter k"),
        ("I", "\u{131}", "Turkish dotless i"),
        ("a", "\u{430}", "Cyrillic a"),
        ("admin", "ad\u{200b}min", "a zero-width space"),
        ("admin", "ad\u{ad}min", "a soft hyphen"),
    ];
    println!(
        "      {:<20} {:<20}{:>7}{:>7}{:>7}{:>8}   what it is",
        "left", "right", "==", "lower", "upper", "asciieq"
    );
    let mut merged = [0usize; 4];
    for (l, r, note) in pairs {
        let got = [
            l == r,
            l.to_lowercase() == r.to_lowercase(),
            l.to_uppercase() == r.to_uppercase(),
            l.eq_ignore_ascii_case(r),
        ];
        let mut row = String::new();
        for (i, &g) in got.iter().enumerate() {
            merged[i] += usize::from(g);
            row.push_str(&format!("{:>width$}", mark(g), width = if i == 3 { 8 } else { 7 }));
        }
        println!(
            "      {:<20} {:<20}{}   {}",
            format!("{l:?}"),
            format!("{r:?}"),
            row,
            note
        );
    }
    let mut totals = String::new();
    for (i, n) in merged.iter().enumerate() {
        totals.push_str(&format!("{:>width$}", n, width = if i == 3 { 8 } else { 7 }));
    }
    println!(
        "      {:<20} {:<20}{}",
        "",
        format!("merged, of {}", pairs.len()),
        totals
    );
    println!();
    let reached = pairs
        .iter()
        .filter(|(l, r, _)| l.to_lowercase() == r.to_lowercase() || l.to_uppercase() == r.to_uppercase())
        .count();
    println!("   No column reaches more than four; between them they reach {reached} of");
    println!("   the sixteen. Nothing std has touches the first row or the fourth:");
    println!("   composing and mark ordering are normalization, std has no");
    println!("   normalize(), and no amount of case conversion is going to help.");
    println!("   The four compatibility rows -- fraction, superscript, fullwidth,");
    println!("   numeral -- are out of reach for the same reason.");
    println!();
    println!("   The rows it does get are split across the two case directions,");
    println!("   and no single direction gets them all:");
    println!();
    for (l, r, note) in [pairs[1], pairs[9], pairs[11], pairs[12]] {
        println!(
            "      {:<12} {:<12} lower {:<6} upper {:<6} {}",
            format!("{l:?}"),
            format!("{r:?}"),
            (l.to_lowercase() == r.to_lowercase()).to_string(),
            (l.to_uppercase() == r.to_uppercase()).to_string(),
            note
        );
    }
    println!();
    println!("   The sharp s merges going UP, because uppercasing it produces");
    println!("   two letters. The KELVIN SIGN merges going DOWN, because its");
    println!("   lowercase is an ordinary k. Fold the other way in either case");
    println!("   and they stay apart. So neither direction of case conversion is");
    println!("   a comparison, and that is what a case FOLD is for: one operation");
    println!("   that catches both, defined so it need not produce a string");
    println!("   anyone would write. Python spells it casefold(). Rust's std has");
    println!("   no spelling for it at all.");
    println!();
    println!("   And the fourth row above is the reason to want the fold rather");
    println!("   than a direction. Uppercasing merges Turkish dotless i onto");
    println!("   ASCII I -- Unicode's default mapping, and nothing to do with a");
    println!("   Turkish locale -- so a program comparing by to_uppercase() has");
    println!("   just decided that two different letters are one. Python's");
    println!("   casefold() keeps them apart. Comparing by uppercasing does not");
    println!("   merge FEWER pairs than a fold; it merges the WRONG ones.");
    println!();

    // ------------------------------------------------------------------ 3
    println!("3. char::to_lowercase RETURNS AN ITERATOR, WHICH IS THE HONEST TYPE");
    bar();
    println!("   One character can case-map to several, so the return type cannot");
    println!("   be char. Rust makes you collect it; Python hides the same fact");
    println!("   behind a str that is quietly longer than the one you passed in.");
    println!();
    let cased = ['\u{df}', '\u{fb01}', '\u{130}', '\u{1e9e}', '\u{1c8}'];
    println!(
        "      {:<10} {:<10} {:<6} {:<12} {:<6} code points of lower",
        "char", "upper", "n(up)", "lower", "n(lo)"
    );
    for c in cased {
        let up: String = c.to_uppercase().collect();
        let lo: String = c.to_lowercase().collect();
        println!(
            "      {:<10} {:<10} {:<6} {:<12} {:<6} {}",
            format!("{c:?}"),
            format!("{up:?}"),
            c.to_uppercase().count(),
            format!("{lo:?}"),
            c.to_lowercase().count(),
            cps(&lo)
        );
    }
    println!();
    println!("   Both n columns reach 2, in different rows: the sharp s and the");
    println!("   ligature grow going up, and LATIN CAPITAL LETTER I WITH DOT");
    println!("   ABOVE grows going down. A program that wrote c.to_uppercase()");
    println!("   and expected a char would not compile, which is the whole");
    println!("   difference between the two languages here -- Python returns a");
    println!("   str either way and lets you find out at the column width.");
    println!();

    // ------------------------------------------------------------------ 4
    println!("4. str::to_lowercase IS NOT A MAP OVER chars");
    bar();
    println!("   The Greek final sigma is decided by POSITION, so the str method");
    println!("   has to look at neighbours -- and it does, where the per-char one");
    println!("   cannot:");
    println!();
    let sigmas = "\u{3a3}\u{3a3}";
    let by_str = sigmas.to_lowercase();
    let by_char: String = sigmas.chars().flat_map(|c| c.to_lowercase()).collect();
    println!("      input                {:<12} {}", format!("{sigmas:?}"), cps(sigmas));
    println!("      str::to_lowercase    {:<12} {}", format!("{by_str:?}"), cps(&by_str));
    println!("      char by char         {:<12} {}", format!("{by_char:?}"), cps(&by_char));
    println!("      same?                {}", by_str == by_char);
    println!();
    println!("   Two capital sigmas lowercase to a medial sigma and a FINAL one,");
    println!("   because the second ends the word. Doing it a character at a time");
    println!("   gives two medial sigmas and a Greek reader a typo. So even the");
    println!("   case operation std does keep is not a per-character table, and");
    println!("   the convenient-looking .chars().flat_map(...) is the wrong loop.");
    println!();

    // ------------------------------------------------------------------ 5
    println!("5. THE SAME FOURTEEN INVISIBLES, AND WHERE THE TWO LANGUAGES PART");
    bar();
    println!("   char::is_whitespace() IS Unicode's White_Space property, and");
    println!("   trim() is defined in terms of it. The Python section above asks");
    println!("   str.isspace() and str.strip() over these same fourteen.");
    println!();
    // The C0 controls have no Unicode name, so the last four names are written
    // down here rather than derived: they are ISO 646 and have not moved.
    let invisible: [(u32, &str); 14] = [
        (0x0020, "SPACE"),
        (0x00A0, "NO-BREAK SPACE"),
        (0x3000, "IDEOGRAPHIC SPACE"),
        (0x2007, "FIGURE SPACE"),
        (0x200B, "ZERO WIDTH SPACE"),
        (0x200C, "ZERO WIDTH NON-JOINER"),
        (0x200D, "ZERO WIDTH JOINER"),
        (0x00AD, "SOFT HYPHEN"),
        (0x2060, "WORD JOINER"),
        (0xFEFF, "ZERO WIDTH NO-BREAK SPACE"),
        (0x001C, "FILE SEPARATOR (FS)"),
        (0x001D, "GROUP SEPARATOR (GS)"),
        (0x001E, "RECORD SEPARATOR (RS)"),
        (0x001F, "UNIT SEPARATOR (US)"),
    ];
    println!("      {:<12} {:<16} {:<10} name", "code point", "is_whitespace", "trimmed");
    for (u, name) in invisible {
        let c = char::from_u32(u).expect("every entry above is a scalar value");
        let padded = format!("x{c}");
        let trimmed = padded.trim() == "x";
        println!(
            "      U+{:04X}       {:<16} {:<10} {}",
            u,
            c.is_whitespace().to_string(),
            if trimmed { "yes" } else { "NO" },
            name
        );
    }
    println!();
    println!("   The first ten rows agree with Python's, value for value. The");
    println!("   last four do not: Python calls all four whitespace and strips");
    println!("   them, and Rust calls none of them whitespace and keeps them.");
    println!();
    println!("   Neither is wrong, and the reason is worth having. Rust asks");
    println!("   Unicode, which does not give White_Space to any C0 control in");
    println!("   that block; Python carries a table of its own that predates the");
    println!("   property and has to stay compatible with itself. So \"trim the");
    println!("   whitespace\" is not one operation across two languages, and the");
    println!("   four characters it disagrees about are the ASCII separators --");
    println!("   reached for as delimiters precisely BECAUSE they are not text.");
    println!("   A record separator that survives a Rust trim and vanishes in a");
    println!("   Python one is a framing bug that only shows up at the seam.");
    println!();

    // ------------------------------------------------------------------ 6
    println!("6. THE ONE ROW RUST CANNOT EVEN HOLD");
    bar();
    println!("   The corpus ends with a lone surrogate, which Python puts in a");
    println!("   str quite happily and refuses only at the encoder. Rust refuses");
    println!("   it at the type:");
    println!();
    for (u, what) in [
        (0xD7FFu32, "the code point just below the surrogates"),
        (0xD800, "the first surrogate"),
        (0xDFFF, "the last surrogate"),
        (0xE000, "the code point just above them"),
        (0x10FFFF, "the highest code point there is"),
        (0x110000, "one past the end"),
    ] {
        println!(
            "      {:<28} is_some {:<6} {}",
            format!("char::from_u32(0x{u:04X})"),
            char::from_u32(u).is_some().to_string(),
            what
        );
    }
    println!();
    let bad = vec![0xEDu8, 0xA0, 0x80];
    match std::str::from_utf8(&bad) {
        Ok(_) => println!("      ED A0 80 decoded, which cannot happen"),
        Err(e) => println!(
            "      str::from_utf8(ED A0 80)   Err, valid_up_to {}, error_len {:?}",
            e.valid_up_to(),
            e.error_len()
        ),
    }
    println!();
    println!("   A char is a Unicode SCALAR VALUE, which is a code point that is");
    println!("   not a surrogate -- so the literal '\\u{{D800}}' is not a value this");
    println!("   program could contain even if it wanted to; it is a compile");
    println!("   error, which is why the bytes are built by hand above.");
    println!();
    println!("   That is the sharpest difference on the page. Python's str holds");
    println!("   the whole code point range and fails at the boundary; Rust's");
    println!("   types hold the encodable subset and fail at construction. Both");
    println!("   are defensible, and a corpus has to know which it is testing:");
    println!("   in Python the lone surrogate is a value your code can carry to");
    println!("   the edge of the system, and in Rust it is three bytes that will");
    println!("   never become a String at all.");
    println!();

    // ------------------------------------------------------------------ 7
    println!("7. THE CORPUS, AS RUST ESCAPES YOU CAN PASTE");
    bar();
    let corpus: [(&str, &str); 18] = [
        ("nfc_nfd", "cafe\u{301}"),
        ("mark_order", "q\u{323}\u{307}"),
        ("singleton", "\u{212b}"),
        ("ligature", "\u{fb01}le"),
        ("superscript", "10\u{b2}"),
        ("fullwidth", "\u{ff21}\u{ff22}"),
        ("sharp_s", "stra\u{df}e"),
        ("final_sigma", "\u{3c2}"),
        ("kelvin", "\u{212a}"),
        ("dotless_i", "\u{131}"),
        ("dotted_i", "\u{130}"),
        ("confusable", "\u{430}"),
        ("zero_width", "ad\u{200b}min"),
        ("soft_hyphen", "ad\u{ad}min"),
        ("nbsp", "a\u{a0}b"),
        ("bom_inside", "a\u{feff}b"),
        ("compat_han", "\u{fa10}"),
        ("expanding", "\u{337f}"),
    ];
    for (name, value) in corpus {
        println!("      let {name:<16} = {};", rust_literal(value));
    }
    println!();
    println!(
        "   {} of the {}. The nineteenth, the lone surrogate, has no line here",
        corpus.len(),
        corpus.len() + 1
    );
    println!("   for the reason section 6 gives -- it cannot be written as a Rust");
    println!("   literal, so a corpus in this language carries it as bytes or not");
    println!("   at all.");
    println!();

    // ------------------------------------------------------------------ 8
    println!("8. WHAT IS MISSING IS A LINE, NOT A GAP");
    bar();
    println!("   std has no normalize() and no casefold(), and it is worth being");
    println!("   clear that this is a decision rather than an omission.");
    println!();
    println!("   std does ship Unicode data: the tables behind a char's own");
    println!("   properties and its case mappings, which is why is_whitespace()");
    println!("   and to_lowercase() work on every script -- and those tables");
    println!("   carry a version, the thing this library keeps out of answer");
    println!("   keys. What std stops short of is the algorithms that look past");
    println!("   one char, and the larger data they need: normalization,");
    println!("   segmentation, locales.");
    println!();
    println!("   So the line is what a char can answer about itself, plus the");
    println!("   one context rule above. Everything past that is a crate:");
    println!("   unicode-normalization for the four forms, caseless or icu for a");
    println!("   fold. The corpus does not get easier in Rust; it gets explicit.");
}
