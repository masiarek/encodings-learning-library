//! The same corpus, in a standard library that declines to guess.
//!
//! Python answers every question this corpus asks, so the Python page reads as
//! "here are the functions". Rust's std answers some of them and has no
//! opinion about the rest, which makes it the better place to see WHICH half
//! is a language's job and which half is a policy the program has to choose.
//!
//! The sixteen pairs below are the same sixteen the Python example uses, in
//! the same order, so the two matrices can be read side by side.
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
    println!("5. WHAT IS MISSING IS A LINE, NOT A GAP");
    bar();
    println!("   std has no normalize() and no casefold(), and it is worth being");
    println!("   clear that this is a decision rather than an omission.");
    println!();
    println!("   Normalization needs a copy of the Unicode tables, and those");
    println!("   tables have a version -- the thing this library keeps out of");
    println!("   answer keys for exactly the same reason. A std that shipped");
    println!("   them would be promising to keep a data file in step with a");
    println!("   language release, forever, for every program that links it.");
    println!();
    println!("   What std does keep is what a char can answer about itself, plus");
    println!("   the one context rule above. Everything past that is a crate:");
    println!("   unicode-normalization for the four forms, caseless or icu for a");
    println!("   fold. The corpus does not get easier in Rust; it gets explicit.");
}
