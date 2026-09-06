//! The same file the dump showed, seen by a type that knows where characters end.
//!
//! A dump hands you every byte and lets you believe any of them is a character.
//! `&str` hands you bytes too — `len()` is a byte count — but it refuses to give
//! you a slice that starts or ends inside one.
//!
//! Run:  rustc --edition 2024 inspecting_a_file_rs.rs && ./inspecting_a_file_rs

fn main() {
    let text = "café: 1€\n";

    println!("1. THE TWO COUNTS A DUMP CANNOT TELL APART");
    println!("   text                {:?}", text);
    println!("   text.len()          {}  <- BYTES, the ls -l number", text.len());
    println!("   chars().count()     {}  <- characters", text.chars().count());
    print!("   as_bytes() in hex   ");
    for b in text.as_bytes() {
        print!("{:02x} ", b);
    }
    println!();
    println!();

    println!("2. WHERE EVERY CHARACTER STARTS — the offsets a dump makes you count by hand");
    for (offset, ch) in text.char_indices() {
        let width = ch.len_utf8();
        let name = if ch == '\n' { "\\n".to_string() } else { ch.to_string() };
        print!("   offset {offset:>2}  {name:<3} U+{:04X}  {width} byte(s)  ", ch as u32);
        let start = offset;
        for b in &text.as_bytes()[start..start + width] {
            print!("{:02x} ", b);
        }
        println!();
    }
    println!();

    println!("3. THE BYTES A DUMP SHOWS THAT ARE NOT CHARACTERS");
    println!("   byte 9 of this file is 0x82. On its own it is not a character at all:");
    println!("   char::from_u32(0x82) = {:?} (a C1 control), and as a UTF-8 fragment", char::from_u32(0x82));
    println!("   it is only ever the middle of the €. Rust will not hand it to you as text:");
    println!("   text.get(9..10) = {:?}   <- None: that range splits a character", text.get(9..10));
    println!("   text.get(8..11) = {:?}    <- Some: the whole €", text.get(8..11));
    println!();

    println!("4. RE-ENCODED TO UTF-16, THE WAY iconv WOULD");
    let units: Vec<u16> = text.encode_utf16().collect();
    println!("   {} code units for {} characters", units.len(), text.chars().count());
    print!("   big-endian bytes    fe ff ");
    for u in &units {
        print!("{:02x} {:02x} ", u >> 8, u & 0xff);
    }
    println!();
    println!("   2 bytes of BOM + {} = {} bytes, where UTF-8 needed {}",
             units.len() * 2, 2 + units.len() * 2, text.len());
    println!();

    println!("5. THE € CODE UNIT, AND WHY A BYTE TOOL CALLS ITS FIRST HALF A SPACE");
    let euro = '€' as u32;
    println!("   '€' is U+{:04X}, so its UTF-16 code unit is 0x{:04X}", euro, euro);
    println!("   written big-endian that is the two bytes {:02x} {:02x}", euro >> 8, euro & 0xff);
    println!("   and 0x{:02x} is also the code point of ' ' — so od -a names it \"sp\"", ' ' as u32);
    println!("   and xxd's text column draws a space. Half a character still looks like a byte.");
}
