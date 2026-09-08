//! The same five strings, and what Rust's type system will and will not count.
//!
//! Rust gives you three of the five rulers for free and names them all
//! differently from Python, which is the useful half of this file: `.len()` is
//! bytes here and code points there, and neither language calls the thing a
//! person means by "character" anything at all.
//!
//! Build:  rustc --edition 2024 a_code_point_is_not_a_character_rs.rs && ./a_code_point_is_not_a_character_rs

// The ladder, same five as the Python file. Every invisible code point is an
// escape: a combining mark and a joiner cannot be read in an editor, so a
// literal would be a claim nobody could check by looking at this file.
const LADDER: [(&str, &str); 5] = [
    ("A", "A"),
    ("cafe + U+0301", "cafe\u{301}"),
    ("nihongo", "\u{65e5}\u{672c}\u{8a9e}"),
    ("grinning face", "\u{1f600}"),
    ("family", "\u{1f468}\u{200d}\u{1f469}\u{200d}\u{1f467}"),
];

const ZWJ: char = '\u{200d}';

/// GB9 approximated by the Combining Diacritical Marks block, plus ZWJ, which
/// UAX #29 also classes as Extend.
fn is_extend(c: char) -> bool {
    matches!(c, '\u{300}'..='\u{36f}') || c == ZWJ
}

/// The same two rules as the Python file: GB9 joins a mark backwards, GB11
/// carries the join across a ZWJ to whatever follows it.
fn graphemes(s: &str) -> usize {
    let mut count = 0usize;
    let mut join_next = false;
    for c in s.chars() {
        if count == 0 || !(join_next || is_extend(c)) {
            count += 1;
        }
        join_next = c == ZWJ;
    }
    count
}

/// The width this program ASSUMES, not one it looks up. Rust's standard
/// library has no East_Asian_Width at all -- see section 4.
fn assumed_width(c: char) -> usize {
    match c {
        '\u{300}'..='\u{36f}' => 0, // combining marks
        '\u{200d}' => 0,            // ZWJ
        '\u{4e00}'..='\u{9fff}' => 2, // CJK ideographs
        '\u{1f300}'..='\u{1faff}' => 2, // emoji
        _ => 1,
    }
}

fn columns(s: &str) -> usize {
    s.chars().map(assumed_width).sum()
}

fn main() {
    println!("1. FIVE RULERS, AND THE THREE RUST HANDS YOU");
    println!("   {:>5} {:>4} {:>5} {:>5} {:>4}   what it is", "bytes", "u16", "chars", "graph", "cols");
    for (label, s) in LADDER {
        println!(
            "   {:>5} {:>4} {:>5} {:>5} {:>4}   {}",
            s.len(),                        // UTF-8 bytes -- this is what len() is
            s.encode_utf16().count(),       // 16-bit units
            s.chars().count(),              // code points
            graphemes(s),                   // this file's two rules
            columns(s),                     // this file's width table
            label
        );
    }
    println!();

    println!("2. THE NAMES ARE THE TRAP");
    println!("   Rust    s.len()             UTF-8 BYTES      -- an O(1) field read");
    println!("   Python  len(s)              CODE POINTS      -- a different question");
    println!("   Rust    s.chars().count()   code points      -- O(n), and it says so");
    println!("   Java    s.length()          UTF-16 units     -- a third answer");
    println!();
    println!("   One spelling, len(), means two different rulers in the two");
    println!("   languages on this page. Rust makes the count you did not ask");
    println!("   for expensive to write by accident: .chars().count() is a");
    println!("   visible walk, where len() is a field on the string.");
    println!();

    println!("3. WHAT THE TYPES ACTUALLY GUARANTEE");
    let family = LADDER[4].1;
    println!("   a &str is guaranteed valid UTF-8, so these two never disagree:");
    println!("     family.len()                 = {}", family.len());
    println!("     family.as_bytes().len()      = {}", family.as_bytes().len());
    println!("   a char is a single code point, always 4 bytes as a value:");
    println!("     size_of::<char>()            = {}", size_of::<char>());
    println!("     family.chars().count()       = {}", family.chars().count());
    println!("   and nothing in the standard library counts the fourth ruler:");
    println!("     family.graphemes()           does not exist");
    println!("     graphemes(family)            = {}   <- the two rules in this file",
             graphemes(family));
    println!();
    println!("   Slicing is where this stops being trivia. &s[0..1] on the");
    println!("   family panics: byte 1 is inside a four-byte character, and Rust");
    println!("   refuses rather than hand back half a code point. Python's");
    println!("   s[0:1] returns the whole emoji, because its index is a code");
    println!("   point index. Neither one can slice off a whole grapheme.");
    println!();

    println!("4. THE FIFTH RULER IS NOT IN THE STANDARD LIBRARY AT ALL");
    println!("   Python at least has unicodedata.east_asian_width() to argue");
    println!("   about. Rust's std has no width property at all, and no");
    println!("   grapheme segmenter. It does carry Unicode tables -- enough for");
    println!("   is_alphabetic(), for a to_uppercase() that turns one letter");
    println!("   into two, and for char::UNICODE_VERSION to have a value -- so");
    println!("   the missing two were left out, not merely never added.");
    println!("   So the 'cols' column above came from the table in this file:");
    println!("     U+0300..U+036F   -> 0   combining marks");
    println!("     U+200D           -> 0   ZWJ");
    println!("     U+4E00..U+9FFF   -> 2   CJK ideographs");
    println!("     U+1F300..U+1FAFF -> 2   emoji");
    println!("     everything else  -> 1");
    println!();
    println!("   Both of the missing rulers need a table that changes every");
    println!("   September, and both have an answer outside std: the");
    println!("   unicode-segmentation crate for rule 4, unicode-width for rule");
    println!("   5. Those are versioned separately from the compiler, which is");
    println!("   the same table skew this library keeps meeting -- moved into a");
    println!("   Cargo.toml, where at least it has a version number you can read.");
}
