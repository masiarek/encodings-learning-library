// Byte order in the type, and the mark std will not remove for you.
//
// Rust writes the two orders as two different methods, so a program that
// serialises a number has to say which one it meant -- there is no default to
// get wrong silently. And on the reading side it shows the other half of this
// page: `String::from_utf8` accepts EF BB BF happily, because a signature IS
// valid UTF-8, and then nothing in std ever takes it off. There is no
// `utf-8-sig` here. The strip is yours to write, and `trim()` will not do it.
//
// Build:  rustc --edition 2024 byte_order_and_bom_rs.rs -o /tmp/bom && /tmp/bom

fn head(n: u32, title: &str) {
    println!("\n{n}. {title}\n{}", "-".repeat(72));
}

fn main() {
    // -------------------------------------------------------------- 1
    head(1, "THE ORDER IS A METHOD NAME, NOT A DEFAULT");
    let n: u32 = 258;
    println!("   let n: u32 = {n};");
    println!("     n.to_be_bytes()  = {:02x?}   big-endian, network order", n.to_be_bytes());
    println!("     n.to_le_bytes()  = {:02x?}   little-endian", n.to_le_bytes());
    println!("     n.to_ne_bytes()  = whichever this machine uses -- not printed here,");
    println!("                        because a recorded answer key must not depend");
    println!("                        on the machine that produced it");
    println!();
    println!("   Three methods, three names. Nothing is implicit, so a program");
    println!("   that writes a number to a socket or a file has already said");
    println!("   which end it meant. `to_ne_bytes` is the one to be suspicious");
    println!("   of: it is correct for a memory dump and wrong for a format.");

    // -------------------------------------------------------------- 2
    head(2, "READING BACK, WITH THE ORDER SUPPLIED BY THE READER");
    let raw = [0x00u8, 0x00, 0x01, 0x02];
    println!("   the four bytes            {raw:02x?}");
    println!("     u32::from_be_bytes(..)  = {}", u32::from_be_bytes(raw));
    println!("     u32::from_le_bytes(..)  = {}", u32::from_le_bytes(raw));
    println!();
    println!("   Same bytes, two answers, both valid. This is the problem the");
    println!("   byte order mark exists to solve for text: put one known code");
    println!("   point at the front and the reader can work the order out");
    println!("   instead of being told it out of band.");

    // -------------------------------------------------------------- 3
    head(3, "A SIGNATURE IS VALID UTF-8, SO NOTHING REJECTS IT");
    let bytes = vec![0xEF, 0xBB, 0xBF, b'i', b'd'];
    println!("   bytes                     {bytes:02x?}");
    let s = String::from_utf8(bytes).expect("a BOM is valid UTF-8");
    println!("   String::from_utf8(..)     Ok({s:?})");
    println!("     s.len()                 {}   <- bytes, and three of them are the mark", s.len());
    println!("     s.chars().count()       {}   <- one invisible char, then i, then d", s.chars().count());
    println!("     s == \"id\"               {}", s == "id");
    println!();
    println!("   The comparison is the bug, and it is silent. `from_utf8`");
    println!("   cannot help: the mark is a legitimate code point and the bytes");
    println!("   are well formed. Validity was never the question.");

    // -------------------------------------------------------------- 4
    head(4, "trim() WILL NOT REMOVE IT");
    let first = s.chars().next().unwrap();
    println!("   first char                {first:?}");
    println!("     first.is_whitespace()   {}", first.is_whitespace());
    println!("     s.trim() == \"id\"        {}", s.trim() == "id");
    println!();
    println!("   U+FEFF is named ZERO WIDTH NO-BREAK SPACE and is not in");
    println!("   Unicode's White_Space property, so `trim` -- which is defined");
    println!("   in terms of that property -- steps straight over it. A field");
    println!("   that was trimmed and still does not match is this.");

    // -------------------------------------------------------------- 5
    head(5, "SO YOU WRITE THE STRIP, AND IT IS ONE LINE");
    println!("   s.strip_prefix('\\u{{feff}}')  {:?}", s.strip_prefix('\u{feff}'));
    println!("   ..unwrap_or(&s) on a clean string leaves it alone:");
    let clean = String::from("id");
    println!("     {:?} -> {:?}", clean, clean.strip_prefix('\u{feff}').unwrap_or(&clean));
    println!();
    println!("   That is Python's `utf-8-sig` in one method call, and having to");
    println!("   type it is the honest version: std does not hide a codec that");
    println!("   silently edits your input. The cost is that you must remember");
    println!("   to do it at every boundary where a file of unknown origin");
    println!("   arrives -- which is the same place you already chose a codec.");
}
