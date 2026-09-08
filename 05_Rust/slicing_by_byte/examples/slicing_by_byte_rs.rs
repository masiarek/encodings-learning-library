// `&s[a..b]` is a BYTE range over a string of characters, so the two ends have
// to land on character boundaries — and that is the one string rule Rust cannot
// check until the program is running.
//
// The panic is caught with catch_unwind so this program can print a table
// instead of dying at its fourth line. That is what catch_unwind is for here and
// nowhere else; `get()` is the answer in real code. See the lesson.
//
// Build & run:  rustc --edition 2024 slicing_by_byte_rs.rs && ./slicing_by_byte_rs

use std::panic;

/// `café` — 5 bytes, 4 characters, and one boundary in the wrong place.
const S: &str = "café";

/// Cut `s` down to at most `budget` bytes without splitting a character.
///
/// std has `str::floor_char_boundary` for this, stable since Rust 1.91 — this
/// is the whole of what it does, written out because the mechanism is the
/// lesson: walk back until the index is a boundary. At most three steps,
/// because no UTF-8 character is longer than four bytes. (Written by hand
/// rather than called, so this example compiles on an older toolchain too.)
fn truncate_to_bytes(s: &str, budget: usize) -> &str {
    if budget >= s.len() {
        return s;
    }
    let mut end = budget;
    while !s.is_char_boundary(end) {
        end -= 1;
    }
    &s[..end]
}

fn main() {
    println!("1. THE RANGE IS BYTES. THE STRING IS CHARACTERS.");
    println!("   {S:?}   len() = {} bytes, chars().count() = {}", S.len(), S.chars().count());
    println!("   bytes           {}", S.as_bytes().iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" "));
    println!("   byte index      0  1  2  3  4");
    println!("   character       c  a  f  <-- é -->");
    println!("   There are five byte positions and only four characters, so one index — 4 —");
    println!("   points at the middle of a character. Every bug on this page is that index.");
    println!();

    println!("2. ASK BEFORE YOU CUT: is_char_boundary");
    println!("   {:<6} {:>14}   {}", "index", "boundary?", "what is there");
    for i in 0..=S.len() {
        let what = if i == S.len() {
            "the end of the string".to_string()
        } else if S.is_char_boundary(i) {
            format!("the start of {:?}", S[i..].chars().next().unwrap())
        } else {
            "a continuation byte, inside a character".to_string()
        };
        println!("   {i:<6} {:>14}   {what}", S.is_char_boundary(i));
    }
    println!("   Note that len() itself is a boundary — the end of a string always is, which");
    println!("   is what makes &s[..s.len()] legal and &s[..s.len()-1] a coin toss.");
    println!();

    println!("3. THE PREDICTION, CHECKED AGAINST WHAT ACTUALLY HAPPENS");
    println!("   Every &S[0..n], with the answer from section 2 beside the outcome.");
    panic::set_hook(Box::new(|_| {})); // the default hook prints to stderr; we want a table
    println!("   {:<12} {:>16} {:>12}   {}", "expression", "boundary says", "outcome", "value");
    let mut all_agreed = true;
    for n in 0..=S.len() {
        let predicted_ok = S.is_char_boundary(n);
        let result = panic::catch_unwind(|| S[0..n].to_string());
        let outcome = match &result {
            Ok(_) => "returned",
            Err(_) => "PANICKED",
        };
        let value = match &result {
            Ok(s) => format!("{s:?}"),
            Err(_) => "-".to_string(),
        };
        if predicted_ok != result.is_ok() {
            all_agreed = false;
        }
        println!("   {:<12} {:>16} {:>12}   {value}", format!("&S[0..{n}]"), predicted_ok, outcome);
    }
    println!("   is_char_boundary predicted every row: {all_agreed}");
    println!("   That is the whole relationship. The panic is not a mystery about UTF-8 —");
    println!("   it is is_char_boundary returning false at a moment when nobody asked it.");
    println!();

    println!("4. AND ONE OTHER WAY TO PANIC, WHICH IS NOT THIS ONE");
    for (label, r) in [
        ("&S[0..99]  past the end", panic::catch_unwind(|| S[0..99].to_string())),
        ("&S[4..3]   backwards", panic::catch_unwind(|| S[4..3].to_string())),
    ] {
        println!("   {label:<26} {}", if r.is_ok() { "returned" } else { "PANICKED" });
    }
    println!("   Same syntax, same panic machinery, different complaint — out of bounds and");
    println!("   start-after-end are ordinary slice errors that &[u8] has too. Only the char");
    println!("   boundary one is about the encoding, and only it survives a correct length.");
    let _ = panic::take_hook();
    println!();

    println!("5. get() ASKS THE SAME QUESTION AND RETURNS AN ANSWER");
    for n in [3usize, 4, 5, 99] {
        println!("   {:<14} {:?}", format!("S.get(0..{n})"), S.get(0..n));
    }
    println!("   Option, not a panic — the same shape as checked_add. Every range that came");
    println!("   from you rather than from std should go through this, and the None case is");
    println!("   a real branch: it means the index was computed by someone counting");
    println!("   characters, or reading a byte budget out of a database column.");
    println!();

    println!("6. WHERE A VALID INDEX COMES FROM");
    println!("   Indices that std produced are ALWAYS boundaries. These all are:");
    println!("     find('f')          {:?}", S.find('f'));
    println!("     char_indices()     {:?}", S.char_indices().map(|(i, _)| i).collect::<Vec<_>>());
    println!("     split('a') pieces  {:?}", S.split('a').collect::<Vec<_>>());
    println!("   An index you computed carries no such guarantee, and the coin lands both");
    println!("   ways on the very same string:");
    let polish = "zażółć gęślą jaźń";
    for (label, i) in [("half of \"café\"", S.len() / 2), ("half of the Polish string", polish.len() / 2)] {
        let src = if label.starts_with("half of \"c") { S } else { polish };
        println!("     {label:<27} index {i:<3} boundary? {}", src.is_char_boundary(i));
    }
    println!("   Two halfway points, one safe and one not, and nothing in either expression");
    println!("   says which. 'the halfway point', 'the first 20 characters' and 'byte 4' are");
    println!("   the three sources of every panic of this kind.");
    println!();

    println!("7. THE FIXED-WIDTH FIELD, DONE PROPERLY");
    let long = "zażółć gęślą jaźń";
    println!("   {long:?}   {} bytes, {} chars", long.len(), long.chars().count());
    println!("   {:<8} {:>7} {:>7}   kept", "budget", "bytes", "chars");
    for budget in [4usize, 5, 6, 10, 20, 99] {
        let cut = truncate_to_bytes(long, budget);
        println!("   {budget:<8} {:>7} {:>7}   {cut:?}", cut.len(), cut.chars().count());
    }
    println!("   Never more than the budget, never a split character, and never a panic.");
    println!("   A budget of 5 keeps 4 bytes because byte 5 is inside 'ż' — so the field is");
    println!("   one byte short of full, which is the correct answer and not a rounding");
    println!("   error. Truncating at exactly N bytes instead writes a file that is no");
    println!("   longer text, and nothing downstream will tell you which record did it.");
}
