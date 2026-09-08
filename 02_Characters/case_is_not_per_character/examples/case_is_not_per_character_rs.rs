//! Case mapping in Rust, where the signature tells you the truth up front.
//!
//! `char::to_uppercase` does not return a `char`. It cannot: `'ß'` uppercases
//! to two characters, so the only honest return type is an iterator. That is
//! the whole lesson, enforced by the compiler rather than documented in a note.
//!
//! And then the sharper half: `char::to_lowercase` and `str::to_lowercase`
//! give different answers for the same text, and the `char` one is the wrong
//! answer -- not from a bug, but because a `char` cannot see its neighbours.
//!
//! Build:  rustc --edition 2024 case_is_not_per_character_rs.rs && ./case_is_not_per_character_rs

fn cps(s: &str) -> String {
    s.chars().map(|c| format!("{:04X}", c as u32)).collect::<Vec<_>>().join(" ")
}

fn rule(title: &str) {
    println!("{title}");
    println!("{}", "-".repeat(72));
}

fn main() {
    // ------------------------------------------------------------------
    rule("1. THE RETURN TYPE IS THE LESSON");
    println!("   fn to_uppercase(self) -> ToUppercase      // not -> char");
    println!("   fn to_lowercase(self) -> ToLowercase      // not -> char");
    println!();
    println!("   Both are iterators of `char`. A function returning one `char`");
    println!("   would be unimplementable, and the reason is a single German");
    println!("   letter:");
    println!();
    println!(
        "   {:<6} {:>3} {:<8} {:<14}  {:>3} {:<10} {}",
        "char", "up", "yields", "code points", "low", "yields", "code points"
    );
    for c in ['ß', 'ﬃ', 'İ', 'A'] {
        let up: String = c.to_uppercase().collect();
        let lo: String = c.to_lowercase().collect();
        println!(
            "   {:<6} {:>3} {:<8} {:<14}  {:>3} {:<10} {}",
            format!("{c:?}"),
            c.to_uppercase().count(),
            format!("{up:?}"),
            cps(&up),
            c.to_lowercase().count(),
            format!("{lo:?}"),
            cps(&lo)
        );
    }
    println!();
    println!("   Sharp s yields two going up. The `ffi` ligature yields three,");
    println!("   which is the ceiling std documents. And U+0130 yields one going");
    println!("   up and TWO going down -- so neither direction is safe to assume,");
    println!("   and `.count()` is never a constant.");
    println!();

    // ------------------------------------------------------------------
    rule("2. THE SAME TEXT, TWO METHODS, TWO ANSWERS");
    let word = "ΟΔΟΣ"; // Greek for `street`, all caps
    let by_str: String = word.to_lowercase();
    let by_char: String = word.chars().flat_map(|c| c.to_lowercase()).collect();
    println!("   input                            {:?}  {}", word, cps(word));
    println!("   str::to_lowercase                {:?}  {}", by_str, cps(&by_str));
    println!("   chars().flat_map(to_lowercase)   {:?}  {}", by_char, cps(&by_char));
    println!();
    println!("   equal?  {}", by_str == by_char);
    println!();
    println!("   The two expressions look like the same operation written two");
    println!("   ways, and the second is the one a reviewer would call the");
    println!("   explicit version. It ends in U+03C3 where the correct Greek");
    println!("   ends in U+03C2, GREEK SMALL LETTER FINAL SIGMA.");
    println!();
    println!("   `char::to_lowercase` is not wrong. It is asked a question that");
    println!("   has no answer: a `char` is one code point with no left and no");
    println!("   right, and whether a sigma is final is a fact about its");
    println!("   neighbours. std says so in its own documentation and always");
    println!("   returns the non-final form.");
    println!();
    println!("   And `str::to_lowercase` only gets it right by looking:");
    for (text, why) in [
        ("ΟΔΟΣ", "sigma at the end of the word"),
        ("ΟΔΟΣΑ", "same sigma, one letter added after it"),
    ] {
        let lo = text.to_lowercase();
        println!("     {:<8} -> {:<8} {:<26} {}", text, lo, cps(&lo), why);
    }
    println!();

    // ------------------------------------------------------------------
    rule("3. THE PART std WILL NOT DO, AND SAYS SO");
    println!("   Turkish lowercases `I` to `ı` (dotless) and uppercases `i` to");
    println!("   `İ` (dotted). Rust gives the language-neutral answer:");
    println!();
    println!("     'I'.to_lowercase()  ->  {:?}", 'I'.to_lowercase().collect::<String>());
    println!("     'i'.to_uppercase()  ->  {:?}", 'i'.to_uppercase().collect::<String>());
    println!();
    println!("   ...and its own docs state that this holds across languages, on");
    println!("   purpose. There is no locale argument to pass, because `str` has");
    println!("   no notion of what language it is holding.");
    println!();
    println!("   Nor is the ASCII shortcut a way out. It is a different function");
    println!("   with a different promise, and the promise is in the name:");
    println!();
    println!("     {:<10} {:<12} {:<12} {}", "text", "ascii_upper", "to_uppercase", "same?");
    for s in ["odos", "straße", "café"] {
        println!(
            "     {:<10} {:<12} {:<12} {}",
            format!("{s:?}"),
            format!("{:?}", s.to_ascii_uppercase()),
            format!("{:?}", s.to_uppercase()),
            s.to_ascii_uppercase() == s.to_uppercase()
        );
    }
    println!();
    println!("   Row 2 is the one to keep. `to_ascii_uppercase` produced");
    println!("   \"STRA\u{df}E\" -- a lowercase German letter standing in the middle");
    println!("   of five capitals -- and did not fail, did not warn, and returned");
    println!("   a perfectly good String. A function that silently declines to do");
    println!("   its job on some of your data is only safe because it said `ascii`");
    println!("   in its name, which is the entire argument for the name.");
    println!();

    // ------------------------------------------------------------------
    rule("4. WHAT THE STANDARD LIBRARY HANDS TO A CRATE");
    println!("   std does the case axis in full and the LANGUAGE axis not at all,");
    println!("   and it names the crate that does: `icu_casemap`, from Unicode.");
    println!();
    println!("   It also suggests writing the sigma rule yourself, using two");
    println!("   `char` predicates -- `is_cased` and `is_case_ignorable`. On the");
    println!("   stable compiler this file is built with, both are unstable and");
    println!("   the code does not compile. The advice is real; the ingredients");
    println!("   are nightly-only. The dated note on the page has the versions.");
    println!();
    println!("   So the split, in one line each:");
    println!("     length   std handles it, and the return type proves it");
    println!("     position std handles it on `str` and cannot on `char`");
    println!("     language std refuses, deliberately, and points at a crate");
}
