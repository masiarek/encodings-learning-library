// Go declares `type rune = int32`. Rust can write the same line, and the
// result checks exactly what Go's does, which is nothing. What makes `char`
// different is not its name: it is a separate type with a door that can say no.
//
// Build & run:  rustc --edition 2024 rune_is_an_int32_rs.rs && ./rune_is_an_int32_rs

use std::any::TypeId;

/// Go's declaration, in Rust. An alias: a second name, not a second type.
type Rune = i32;

/// Five byte strings no UTF-8 decoder may accept. Glyphs go LAST on each row:
/// `😀` is two terminal columns wide, and a glyph mid-row would bend the columns.
const CASES: [(&[u8], &str); 5] = [
    (b"\xc3", "é cut after 1 of its 2 bytes"),
    (b"\xe2\x82", "€ cut after 2 of its 3 bytes"),
    (b"\xf0\x9f\x98", "😀 cut after 3 of its 4 bytes"),
    (b"\xed\xa0\x80", "U+D800 in the shape of UTF-8"),
    (b"\xf4\x90\x80\x80", "one past U+10FFFF, same shape"),
];

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    println!("1. A RUNE IN RUST IS ONE LINE, AND IT CHECKS NOTHING");
    println!("   type Rune = i32;");
    println!("   TypeId::of::<Rune>() == TypeId::of::<i32>()   {}", TypeId::of::<Rune>() == TypeId::of::<i32>());
    println!("   TypeId::of::<char>() == TypeId::of::<u32>()   {}", TypeId::of::<char>() == TypeId::of::<u32>());
    println!("   The alias is gone before anything can ask about it: a Rune IS an i32,");
    println!("   the way Go's rune is an int32. A char is not a name for u32. It is a");
    println!("   type of its own, and the only way in is a constructor that can say no.");
    println!();
    println!("   {:>10}   {:>10}   {}", "value", "as a Rune", "as a char");
    for r in [-1, 0x41, 0xE9, 0xD800, 0x10FFFF, 0x110000] {
        let r: Rune = r;
        let as_char = match u32::try_from(r) {
            Err(_) => "refused before char is asked: no u32 is negative".to_string(),
            Ok(u) => match char::from_u32(u) {
                Some(c) => format!("Some(U+{:04X})", c as u32),
                None => "None".to_string(),
            },
        };
        let shown = if r < 0 { format!("{r}") } else { format!("{r:#X}") };
        println!("   {shown:>10}   {r:>10}   {as_char}");
    }
    println!("   All six are Runes, because every i32 is. Three of them are not a char,");
    println!("   and nothing in a Rune says which three.");
    println!();
    println!("   size_of::<Option<Rune>>()   {}   <- no value is off limits, so None needs a tag", size_of::<Option<Rune>>());
    println!("   size_of::<Option<char>>()   {}   <- None is kept in a value no char may hold", size_of::<Option<char>>());
    println!();

    println!("2. THE SAME FIVE MISTAKES, HANDED BACK AS SLICES");
    println!("   {:<12} {:<20} {:>6} {:>9}   {}", "bytes", "invalid chunks", "lossy", "per byte", "what they are");
    for (data, what) in CASES {
        let chunks: Vec<&[u8]> = data.utf8_chunks().map(|c| c.invalid()).filter(|b| !b.is_empty()).collect();
        let lossy = String::from_utf8_lossy(data).matches(char::REPLACEMENT_CHARACTER).count();
        let per_byte: usize = chunks.iter().map(|c| c.len()).sum();
        let shown = chunks.iter().map(|c| format!("[{}]", hex(c))).collect::<Vec<_>>().join(" ");
        println!("   {:<12} {:<20} {:>6} {:>9}   {what}", hex(data), shown, lossy, per_byte);
    }
    println!("   utf8_chunks() walks the original bytes and hands each mistake back as a");
    println!("   slice of them. from_utf8_lossy writes one U+FFFD per slice, because each");
    println!("   slice is one maximal subpart -- the same count the Python example gets");
    println!("   from its own decoder. Add up the slice LENGTHS instead and you have what");
    println!("   Go's `for range` loop writes. A decoder has to know how long a mistake is");
    println!("   to carry on after it, so the per-byte count is never lost -- only rounded");
    println!("   down to one.");
}
