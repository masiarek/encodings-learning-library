//! The same 10-byte field, in a language where "not text" is a type error.
//!
//! Python hands you a `str` with whatever `errors=` said and lets the program
//! carry on. Rust will not build a `String` out of a cut sequence at all, and
//! the error it hands back instead is the interesting part: it separates
//! "these bytes are wrong" from "you cut me in half" as two different VALUES,
//! where Python separates them only as two different sentences.
//!
//! `floor_char_boundary` is std, stabilized in Rust 1.91; the hand-rolled walk
//! beside it is what the same code looks like on an older compiler, and in C.
//!
//! Run:  rustc --edition 2024 fixed_width_byte_fields_rs.rs && ./fixed_width_byte_fields_rs

const VALUE: &str = "zażółć gęślą jaźń";

fn hexs(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

/// Back up while the first dropped byte is a continuation byte (10xxxxxx).
fn floor_by_hand(b: &[u8], width: usize) -> usize {
    let mut n = width.min(b.len());
    while n > 0 && n < b.len() && b[n] & 0b1100_0000 == 0b1000_0000 {
        n -= 1;
    }
    n
}

fn main() {
    let raw = VALUE.as_bytes();

    println!("1. THE SAME ARITHMETIC, IN THE TYPE THAT ENFORCES IT");
    println!("{}", "-".repeat(70));
    println!("   VALUE.len()            {} bytes      <- len() is BYTES on a &str", raw.len());
    println!("   VALUE.chars().count()  {} characters  <- and this one is O(n)", VALUE.chars().count());
    println!("   'ż'.len_utf8()          {}", 'ż'.len_utf8());
    println!();
    println!("   A &str is UTF-8 by definition, so the byte length is the");
    println!("   field width and the character count is what the user typed.");
    println!("   Rust makes you pick which one you meant at every call site.");
    println!();

    println!("2. WHICH WIDTHS ARE BOUNDARIES");
    println!("{}", "-".repeat(70));
    print!("     ");
    let widths: Vec<String> = (1..=raw.len()).map(|n| format!("{n:2}")).collect();
    println!("{}", widths.join(" "));
    print!("     ");
    let marks: Vec<String> = (1..=raw.len())
        .map(|n| format!(" {}", if VALUE.is_char_boundary(n) { '.' } else { 'X' }))
        .collect();
    println!("{}", marks.join(" "));
    let bad: Vec<usize> = (1..=raw.len()).filter(|&n| !VALUE.is_char_boundary(n)).collect();
    println!("   is_char_boundary says {} of {} widths cut inside a character:", bad.len(), raw.len());
    println!("   {bad:?}");
    println!("   The same map the Python run prints, from a different library.");
    println!();

    println!("3. THE THREE WAYS TO ASK FOR A PREFIX");
    println!("{}", "-".repeat(70));
    let w = 13usize;
    println!("   at width {w}, which is not a boundary:");
    println!();
    println!("   VALUE.get(..{w})                {:?}", VALUE.get(..w));
    // Silence the panic hook first: its message names this file's path on
    // this machine, which is not something an answer key may hold.
    let hook = std::panic::take_hook();
    std::panic::set_hook(Box::new(|_| {}));
    let panicked = std::panic::catch_unwind(|| &VALUE[..w]).is_err();
    std::panic::set_hook(hook);
    println!("   &VALUE[..{w}]                   panicked: {panicked}");
    println!("   VALUE.floor_char_boundary({w})  {}", VALUE.floor_char_boundary(w));
    println!("   floor_by_hand(raw, {w})         {}", floor_by_hand(raw, w));
    println!();
    println!("   `get` returns None -- a value you can handle. The index");
    println!("   operator panics, because a &str that is not UTF-8 is a");
    println!("   contradiction rather than an error case, and there is no");
    println!("   value it could return. The two boundary functions agree,");
    println!("   which is the point of showing the hand-rolled one.");
    println!();

    println!("4. WHAT `from_utf8` SAYS ABOUT A CUT SEQUENCE");
    println!("{}", "-".repeat(70));
    let cut = &raw[..w];
    println!("   the bytes            {}", hexs(cut));
    match std::str::from_utf8(cut) {
        Ok(s) => println!("   decoded              {s:?}"),
        Err(e) => {
            println!("   Err(Utf8Error)");
            println!("     valid_up_to()      {}", e.valid_up_to());
            println!("     error_len()        {:?}", e.error_len());
            println!("     the valid prefix   {:?}", std::str::from_utf8(&cut[..e.valid_up_to()]).unwrap());
        }
    }
    println!();
    // Built at runtime rather than written as a literal: rustc's
    // `invalid_from_utf8` lint reads a literal and warns before the program
    // has made its point.
    let genuinely_bad: Vec<u8> = vec![0x7a, 0x61, 0xc5, 0x41, 0x7a];
    let genuinely_bad = genuinely_bad.as_slice();
    match std::str::from_utf8(genuinely_bad) {
        Ok(_) => println!("   (unreachable)"),
        Err(e) => {
            println!("   and for bytes that are wrong rather than cut short:");
            println!("     {}          valid_up_to() {}  error_len() {:?}", hexs(genuinely_bad), e.valid_up_to(), e.error_len());
        }
    }
    println!();
    println!("   error_len() is None for exactly one reason: the input ended");
    println!("   in the middle of a sequence that was otherwise fine. That is");
    println!("   the truncation signature, and it is a VALUE -- so a reader");
    println!("   can say 'this record was cut, ask for more bytes' and mean");
    println!("   something different by 'this record is corrupt'. Python");
    println!("   distinguishes the same two cases only in the text of");
    println!("   UnicodeDecodeError.reason; .start and .end are identical for");
    println!("   both, and the text is a diagnostic that may be reworded.");
    println!();

    println!("5. THE LOSSY READER, AND WHAT IT COSTS");
    println!("{}", "-".repeat(70));
    let lossy = String::from_utf8_lossy(cut);
    println!("   from_utf8_lossy      {lossy:?}");
    println!("     characters           {}", lossy.chars().count());
    println!("     bytes if re-encoded  {}", lossy.as_bytes().len());
    println!("     U+FFFD in it         {}", lossy.chars().filter(|&c| c == '\u{FFFD}').count());
    println!();
    println!("   One replacement character stands in for the one byte that");
    println!("   was left behind, and it costs three bytes to write. So the");
    println!("   repaired value is LONGER than the field it came out of --");
    println!("   which is how a lossy read of a fixed-width file overflows");
    println!("   the very column it is being loaded into.");
    println!();

    println!("6. CUTTING BY CHARACTERS INSTEAD");
    println!("{}", "-".repeat(70));
    let mut used = 0usize;
    let mut end = 0usize;
    for (i, ch) in VALUE.char_indices() {
        let n = ch.len_utf8();
        if used + n > w {
            break;
        }
        used += n;
        end = i + n;
    }
    println!("   char_indices() walk   {:?}  ({} bytes)", &VALUE[..end], end);
    println!("   floor_char_boundary   {:?}  ({} bytes)", &VALUE[..VALUE.floor_char_boundary(w)], VALUE.floor_char_boundary(w));
    println!();
    println!("   Same answer. Reach for floor_char_boundary when you have a");
    println!("   byte budget and the walk when you also need the count, the");
    println!("   offsets, or a rule about which characters may be dropped.");
}
