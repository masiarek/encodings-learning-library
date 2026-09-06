//! What Rust's standard library will and will not do about two spellings.
//!
//! Every accented literal here is written with `\u{...}` escapes rather than
//! pasted, for the reason the Python example opens with: a pasted decomposed
//! string may not survive the trip into the file.

const RULE: &str = "------------------------------------------------------------------------";

fn cps(s: &str) -> String {
    s.chars()
        .map(|c| format!("U+{:04X}", c as u32))
        .collect::<Vec<_>>()
        .join(" ")
}

/// The whole of NFD for five Latin letters. The algorithm is a table lookup;
/// the table is the part that is not five entries long.
fn naive_nfd(s: &str) -> String {
    let mut out = String::new();
    for c in s.chars() {
        match c {
            '\u{e9}' => out.push_str("e\u{301}"), // é
            '\u{f3}' => out.push_str("o\u{301}"), // ó
            '\u{17c}' => out.push_str("z\u{307}"), // ż
            '\u{c5}' => out.push_str("A\u{30a}"), // Å
            '\u{f1}' => out.push_str("n\u{303}"), // ñ
            other => out.push(other),
        }
    }
    out
}

fn main() {
    let composed = "caf\u{e9}";
    let decomposed = "cafe\u{301}";

    println!("1. THE TYPE SYSTEM DOES NOT HELP HERE");
    println!("{RULE}");
    println!("   Both of these are a &str, both are valid UTF-8, and both");
    println!("   print as the same word:");
    println!();
    println!("   composed     {}   {:>2} bytes  {} chars  {}",
             composed, composed.len(), composed.chars().count(), cps(composed));
    println!("   decomposed   {}   {:>2} bytes  {} chars  {}",
             decomposed, decomposed.len(), decomposed.chars().count(), cps(decomposed));
    println!();
    println!("   composed == decomposed            {}", composed == decomposed);
    println!();
    println!("   `String` promises the bytes are valid UTF-8. It promises");
    println!("   nothing at all about WHICH valid sequence you got, and == is");
    println!("   a byte comparison, so the answer above is correct and useless.");
    println!();

    println!("2. STD DOES THE CASE AXIS, IN FULL");
    println!("{RULE}");
    println!("   char  to_lowercase  to_uppercase  note");
    for c in ['\u{df}', '\u{1e9e}', '\u{130}'] {
        let (lo, up): (String, String) = (c.to_lowercase().collect(), c.to_uppercase().collect());
        let note = match c {
            '\u{df}' => "one char in, two out",
            '\u{1e9e}' => "capital sharp S lowercases to the small one",
            _ => "and this one GROWS A COMBINING MARK",
        };
        println!("   {:<5} {:<13} {:<13} {}", c, lo, up, note);
    }
    println!();
    println!("   The last row is the trap, and it is not Python's:");
    println!();
    println!("     '\\u{{130}}'.to_lowercase()  ->  {}",
             cps(&'\u{130}'.to_lowercase().collect::<String>()));
    println!();
    println!("   Lowercasing produced a combining mark that was not in the");
    println!("   input, so lowercase-then-compare has the same ordering");
    println!("   problem in Rust as it has everywhere else.");
    println!();

    println!("3. AND STD DOES NOT DO THE NORMALIZATION AXIS AT ALL");
    println!("{RULE}");
    println!("   There is no `str::normalize`. The one caseless comparison in");
    println!("   std is ASCII-only, and says so in its name:");
    println!();
    println!("     \"CAF\u{c9}\".eq_ignore_ascii_case(\"caf\u{e9}\")   {}",
             "CAF\u{c9}".eq_ignore_ascii_case("caf\u{e9}"));
    println!("     \"CAFE\".eq_ignore_ascii_case(\"cafe\")   {}",
             "CAFE".eq_ignore_ascii_case("cafe"));
    println!();
    println!("   That is not a gap somebody forgot. Normalization needs the");
    println!("   Unicode decomposition tables, and Rust keeps its standard");
    println!("   library free of data that has a yearly release. The crate is");
    println!("   `unicode-normalization`, and it is the answer.");
    println!();

    println!("4. WHAT THE CRATE IS ACTUALLY CARRYING");
    println!("{RULE}");
    println!("   The algorithm fits on a screen. Here is NFD for five letters:");
    println!();
    for word in ["caf\u{e9}", "\u{17c}\u{f3}\u{142}w", "\u{c5}ngstr\u{f6}m"] {
        let d = naive_nfd(word);
        println!("     {:<10} -> {:<12} {}", word, d, cps(&d));
    }
    println!();
    println!("   It is right on the first two words and wrong on the third:");
    println!("   \u{f6} is not in the table, so it comes through composed. That is");
    println!("   the whole difficulty in one line -- not the loop, the data.");
    println!();
    println!("   A real implementation adds three things this has none of:");
    println!("     - every decomposable code point, not five");
    println!("     - canonical ordering, so two marks on one letter sort into");
    println!("       a fixed order and compare equal");
    println!("     - composition exclusions, for the NFC direction");
    println!();
    println!("   Which is why you take the crate. The point of writing the");
    println!("   loop is to see that the table is the library.");
}
