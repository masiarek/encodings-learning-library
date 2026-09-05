// Rust does not have an opinion about overlong sequences. It has a type.
//
// `&str` is defined as well-formed UTF-8, so an overlong brace cannot be
// inside one -- not as a bug you have to look for, but as a thing that
// cannot be constructed. This program shows where the refusal happens, how
// precisely the error points at it, and where you can hand the guarantee back.

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02X}")).collect::<Vec<_>>().join(" ")
}

fn main() {
    // The closing brace from the slide, in one, two, three and four bytes.
    let forms: [&[u8]; 4] = [
        &[0x7D],
        &[0xC1, 0xBD],
        &[0xE0, 0x81, 0xBD],
        &[0xF0, 0x80, 0x81, 0xBD],
    ];

    println!("1. from_utf8 ON EACH SPELLING");
    for bytes in forms {
        match std::str::from_utf8(bytes) {
            Ok(s) => println!("   {:<12} Ok({s:?})", hex(bytes)),
            Err(e) => println!(
                "   {:<12} Err(valid_up_to: {}, error_len: {:?})",
                hex(bytes),
                e.valid_up_to(),
                e.error_len()
            ),
        }
    }
    println!("   valid_up_to is how many bytes were text before the trouble -- zero here,");
    println!("   because the trouble is the first byte of the sequence. error_len is how");
    println!("   many bytes to skip: Some(1) means one bad byte, then look again.");

    println!("\n2. THE SAME BYTES, MADE SAFE INSTEAD OF REFUSED");
    for bytes in forms {
        let lossy = String::from_utf8_lossy(bytes);
        println!(
            "   {:<12} -> {lossy:?}   ({} replacement char{})",
            hex(bytes),
            lossy.chars().filter(|c| *c == '\u{FFFD}').count(),
            if lossy.chars().filter(|c| *c == '\u{FFFD}').count() == 1 { "" } else { "s" }
        );
    }
    println!("   Lossy conversion never invents the brace. It marks the damage and moves on,");
    println!("   one U+FFFD per byte that could not begin or continue a real sequence.");

    println!("\n3. THE CHARACTER WAS NEVER THE PROBLEM");
    println!("   char::from_u32(0x7D)      = {:?}", char::from_u32(0x7D));
    println!("   '}}' encodes as             {}", hex('}'.to_string().as_bytes()));
    println!("   char::from_u32(0xD800)    = {:?}   (a surrogate is not a character)", char::from_u32(0xD800));
    println!("   char::MAX                 = U+{:04X}", char::MAX as u32);
    println!("   U+007D is a perfectly good code point with a perfectly good encoding.");
    println!("   What Rust refused was a second, longer way of writing the same one.");

    println!("\n4. WHERE THE GUARANTEE IS HANDED BACK");
    // from_utf8_unchecked skips the check. Used on bytes that really are
    // well-formed, it is sound -- the promise is true, so nothing is lost.
    let honest: &[u8] = &[0x7D];
    let s: &str = unsafe { std::str::from_utf8_unchecked(honest) };
    println!("   from_utf8_unchecked({}) = {s:?}   -- sound: the bytes really are UTF-8", hex(honest));
    println!("   The same call on C1 BD would be undefined behaviour, and this program");
    println!("   does not make it: every later &str method is allowed to assume the");
    println!("   invariant, so a false promise is not a wrong answer, it is no answer.");
    println!("   Write that line with the bytes in view and rustc refuses to compile it --");
    println!("   see the page for the error. `unsafe` moves the check to you; it does not");
    println!("   remove it, and here the compiler checks your homework anyway.");
}
