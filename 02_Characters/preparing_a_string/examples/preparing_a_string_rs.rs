// Rust has no stringprep, no IDNA and no normalization in std -- so this
// program does the one step of RFC 3454 that needs no table beyond the RFC's
// own list, and then says plainly what the other three would cost.
//
// Table B.1, "commonly mapped to nothing", is 27 code points written out in
// the document. That makes it the rare Unicode table a program may carry as a
// literal: it cannot drift, because it was frozen in 2002 along with the rest
// of the RFC. Everything below is therefore the same on every machine.
//
// The compiler settles this before the program runs:
const _: () = assert!(char::UNICODE_VERSION.0 > 3);

/// RFC 3454 appendix B.1 -- delete these, whatever else you do.
const MAPPED_TO_NOTHING: [char; 27] = [
    '\u{00AD}', // SOFT HYPHEN
    '\u{034F}', // COMBINING GRAPHEME JOINER
    '\u{1806}', // MONGOLIAN TODO SOFT HYPHEN
    '\u{180B}', '\u{180C}', '\u{180D}', // MONGOLIAN FREE VARIATION SELECTORs
    '\u{200B}', // ZERO WIDTH SPACE
    '\u{200C}', // ZERO WIDTH NON-JOINER
    '\u{200D}', // ZERO WIDTH JOINER
    '\u{2060}', // WORD JOINER
    '\u{FE00}', '\u{FE01}', '\u{FE02}', '\u{FE03}', '\u{FE04}', '\u{FE05}',
    '\u{FE06}', '\u{FE07}', '\u{FE08}', '\u{FE09}', '\u{FE0A}', '\u{FE0B}',
    '\u{FE0C}', '\u{FE0D}', '\u{FE0E}', '\u{FE0F}', // VARIATION SELECTOR-1..16
    '\u{FEFF}', // ZERO WIDTH NO-BREAK SPACE -- the BOM, in the middle of a string
];

fn map_to_nothing(s: &str) -> String {
    s.chars().filter(|c| !MAPPED_TO_NOTHING.contains(c)).collect()
}

fn bar() {
    println!("{}", "-".repeat(72));
}

fn main() {
    println!("\n1. THE ONE STEP THAT IS JUST A LIST");
    bar();
    println!("   RFC 3454 table B.1, transcribed:  {} code points", MAPPED_TO_NOTHING.len());
    println!("   the widest one                    U+{:04X}", MAPPED_TO_NOTHING.iter().map(|c| *c as u32).max().unwrap());
    println!();
    println!("   A table small enough to write down is a table that cannot rot.");
    println!("   This one was sealed with the RFC in 2002, so a Rust literal is");
    println!("   an honest way to carry it -- which is NOT true of any of the");
    println!("   other three steps.");

    println!("\n2. STRINGS THAT LOOK IDENTICAL AND ARE NOT");
    bar();
    let probes: [(&str, String); 4] = [
        ("nothing inserted", "admin".to_string()),
        ("U+200B ZERO WIDTH SPACE", format!("ad{}min", '\u{200B}')),
        ("U+00AD SOFT HYPHEN", format!("ad{}min", '\u{00AD}')),
        ("U+FEFF the BOM, mid-string", format!("ad{}min", '\u{FEFF}')),
    ];
    println!("   {:<28} {:>5} {:>5}  {:<10} {}", "stored as", "chars", "bytes", "== \"admin\"", "after B.1");
    for (label, stored) in &probes {
        println!(
            "   {:<28} {:>5} {:>5}  {:<10} {}",
            label,
            stored.chars().count(),
            stored.len(),
            stored == "admin",
            if map_to_nothing(stored) == "admin" { "== \"admin\"" } else { "still not" }
        );
    }
    println!();
    println!("   Every row renders as `admin` in every font there is. Three of");
    println!("   them are longer, and `==` on &str compares bytes -- so they are");
    println!("   four different names to Rust and one name to the person who");
    println!("   typed them. Deleting B.1 first is what closes that gap, and it");
    println!("   is step one of four for exactly this reason.");

    println!("\n3. WHAT RUST'S std WILL AND WILL NOT DO FOR YOU");
    bar();
    println!("   the case axis, in full:");
    println!("      'ß'.to_uppercase()        {:?}   ({} chars)", 'ß'.to_uppercase().to_string(), 'ß'.to_uppercase().count());
    println!("      \"CAFÉ\".to_lowercase()     {:?}", "CAFÉ".to_lowercase());
    println!("      eq_ignore_ascii_case      {}   <- and it says its limit in its name", "CAFÉ".eq_ignore_ascii_case("café"));
    println!();
    println!("   the normalization axis, not at all:");
    println!("      no normalize() in std, so the two spellings of café stay");
    println!("      two different &str values forever");
    println!();
    println!("   the prohibition axis, partly, and by a different question:");
    for c in ['\u{E000}', '\u{FFFE}', '\u{202E}', '\u{0041}'] {
        println!(
            "      U+{:04X}  char::from_u32 {:<7} is_control {:<7} is_alphabetic {}",
            c as u32,
            char::from_u32(c as u32).is_some(),
            c.is_control(),
            c.is_alphabetic()
        );
    }
    println!();
    println!("   Read the third row. U+202E is not a control character to Rust,");
    println!("   is a perfectly good char, and reverses your terminal. std has");
    println!("   no vocabulary for `this character is fine and must not appear");
    println!("   in an identifier` -- that judgement is the RFC's, not the");
    println!("   language's, and no amount of type safety supplies it.");

    println!("\n4. THE TABLE IS THE LIBRARY");
    bar();
    println!("   Three of the four steps need a table nobody would transcribe:");
    println!("   B.2 is the case-folding database, normalization is the");
    println!("   decomposition database, and C.* plus D.* are properties of");
    println!("   every assigned code point. In Rust each is a crate -- and what");
    println!("   the crate ships is data, not cleverness.");
    println!();
    println!("   That is why the version question follows preparation around.");
    println!("   A hand-written B.1 is fixed forever; a hand-written B.2 is a");
    println!("   snapshot of somebody's Unicode, and the RFC pinned 3.2 rather");
    println!("   than let it move underneath a domain name.");
    println!();
    println!("   Is this compiler's table newer than the RFC's 3.2?  {}", char::UNICODE_VERSION.0 > 3);
    println!("   By how much is deliberately not printed -- that would put the");
    println!("   machine that built this page into the answer key.");
}
