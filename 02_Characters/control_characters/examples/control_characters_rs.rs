// Control characters in Rust: escapes in literals, `is_control`, and what {:?} shows.
//
// Build & run:  rustc --edition 2024 control_characters_rs.rs && ./control_characters_rs

fn main() {
    println!("1. THE ESCAPES A LITERAL ACCEPTS");
    let s = "tab\there\nnew line\r\ncrlf\0nul\x1bESC";
    println!("   {:?}", s);
    println!("   {} bytes, {} chars — the escapes are single bytes once compiled", s.len(), s.chars().count());
    println!("   (Rust has no \\a \\b \\f \\v: write \\x07 \\x08 \\x0C \\x0B)");
    println!();

    println!("2. TWO QUESTIONS, TWO METHODS");
    for c in ['\t', '\n', '\r', '\0', '\x1b', '\x7f', 'A', '\u{85}', '\u{2028}'] {
        println!(
            "   {:<10} U+{:04X}  is_ascii_control={:<5} is_control={}",
            format!("{c:?}"), c as u32, c.is_ascii_control(), c.is_control()
        );
    }
    println!("   is_ascii_control is the 0..=31 + 127 table; is_control is Unicode's Cc category, which adds 0x80..=0x9F.");
    println!();

    println!("3. lines() SPLITS ON \\n AND STRIPS A TRAILING \\r — AND ON NOTHING ELSE");
    let text = "one\r\ntwo\nthree\rfour";
    let lines: Vec<&str> = text.lines().collect();
    println!("   {:?}", text);
    println!("   lines() -> {:?}", lines);
    println!("   (the lone \\r in 'three\\rfour' is not a line end to Rust)");
    println!();

    println!("4. THE CARET ARITHMETIC");
    for letter in [b'I', b'J', b'M', b'['] {
        let ctrl = letter & 0x1F;
        println!("   Ctrl-{}  = {:#04x} & 0x1F = {:>2} = {:?}", letter as char, letter, ctrl, ctrl as char);
    }
    println!();

    println!("5. NUL IS A CHARACTER TO RUST, TOO — UNTIL IT MEETS C");
    let with_nul = "ab\0cd";
    println!("   {:?}.len() = {}", with_nul, with_nul.len());
    println!("   std::ffi::CString::new({:?}) -> {:?}", with_nul, std::ffi::CString::new(with_nul).map(|_| ()));
    println!("   Rust refuses to make a C string with an interior NUL, because C would silently truncate it.");
}
