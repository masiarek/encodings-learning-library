// The gate is ASCII-narrow and correct. The stage after it is Unicode-wide.
//
// Bare rustc, no crates -- which is itself half the lesson: `to_lowercase` is in
// std and NFKC is not, so on a Rust codebase the canonicalisation step is a
// dependency, and dependencies run wherever somebody happened to call them.

fn banner(n: u32, title: &str) {
    println!("{}. {}", n, title);
}

/// Every char as U+XXXX. A Debug print of "\u{212A}elvin" comes out looking
/// exactly like the ASCII word, which is the bug rather than a way to show it.
fn codepoints(s: &str) -> String {
    s.chars().map(|c| format!("U+{:04X}", c as u32)).collect::<Vec<_>>().join(" ")
}

fn main() {
    let reserved = "kelvin";
    let candidate = "\u{212A}elvin"; // U+212A KELVIN SIGN, then "elvin"

    banner(1, "THE GATE IS CORRECT, AND ASCII-NARROW");
    println!("   reserved name      {reserved:?}");
    println!("   candidate          {candidate:?}   ({} chars, {} bytes)",
             candidate.chars().count(), candidate.len());
    println!("   ...which is         {}", codepoints(candidate));
    println!("   ...written as       \"\\u{{212A}}elvin\"");
    println!("   Printed, it is indistinguishable from the ASCII word. That is");
    println!("   not a limitation of this program; it is the entire technique.");
    println!("   to_ascii_lowercase {:?}", candidate.to_ascii_lowercase());
    println!("   equal to reserved? {}", candidate.to_ascii_lowercase() == reserved);
    println!("   eq_ignore_ascii_case? {}", candidate.eq_ignore_ascii_case(reserved));
    println!("   So the registration is allowed, and every line above is right:");
    println!("   U+212A is not an ASCII letter and an ASCII fold must not touch it.");
    println!();

    banner(2, "THE STAGE AFTER IT IS NOT NARROW");
    println!("   to_lowercase       {:?}", candidate.to_lowercase());
    println!("   equal to reserved? {}", candidate.to_lowercase() == reserved);
    println!("   Full Unicode lowercasing maps U+212A KELVIN SIGN to ASCII 'k'.");
    println!("   Two accounts now canonicalise to one name. Which of them the");
    println!("   next lookup returns is a question about a hash table, not policy.");
    println!();

    banner(3, "AND CASE MAPPING CHANGES LENGTH");
    for s in ["\u{df}", "\u{fb01}", "\u{130}"] {
        let up = s.to_uppercase();
        let low = s.to_lowercase();
        println!("   {:?}  {} chars {:>2} bytes  ->  upper {:?} {} chars   lower {:?} {} chars",
                 s, s.chars().count(), s.len(),
                 up, up.chars().count(), low, low.chars().count());
    }
    println!("   A length limit checked BEFORE a case fold does not hold after it.");
    println!("   Both directions exist: 'fi' as one ligature grows, and a string");
    println!("   trimmed to fit can be cut through the middle of a character.");
    println!();

    banner(4, "WHAT std GIVES YOU, AND WHAT IT DOES NOT");
    println!("   to_lowercase / to_uppercase   full Unicode, in std");
    println!("   to_ascii_lowercase            ASCII only, and the name says so");
    println!("   eq_ignore_ascii_case          ASCII only, and the name says so");
    println!("   NFC / NFD / NFKC / NFKD       not in std at all -- a crate");
    println!("   Rust names its narrow operations honestly, which is a real");
    println!("   advantage: you cannot reach for an ASCII fold by accident.");
    println!("   But the wide one is a dependency, so the compiler has no opinion");
    println!("   about WHERE it runs -- and where it runs is the whole question.");
    println!();

    banner(5, "THE ORDER THAT WORKS");
    let canonical = candidate.to_lowercase();
    println!("   let canonical = input.to_lowercase();      // canonicalise");
    println!("   if canonical == reserved {{ reject() }}       // then check");
    println!("   store(&canonical);                         // then store THAT");
    println!("   canonical = {canonical:?} ({})  -> rejected: {}",
             codepoints(&canonical), canonical == reserved);
    println!("   The third line is the one people leave out. Checking the");
    println!("   canonical form and storing the original puts the two spellings");
    println!("   back in the database, and the next lookup gets to choose.");
}
