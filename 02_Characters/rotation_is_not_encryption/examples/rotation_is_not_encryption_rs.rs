//! ROT13 in Rust: a byte sum while the text is ASCII, and a type that refuses
//! to keep counting once it is not.
//!
//! Run:  rustc --edition 2024 rotation_is_not_encryption_rs.rs -o /tmp/rot && /tmp/rot

/// Rotate ASCII letters by n. Bytes outside A-Za-z are copied unchanged.
fn rot_ascii(s: &str, n: u8) -> String {
    s.bytes()
        .map(|b| match b {
            b'a'..=b'z' => (b - b'a' + n) % 26 + b'a',
            b'A'..=b'Z' => (b - b'A' + n) % 26 + b'A',
            other => other,
        })
        .map(char::from)
        .collect()
}

fn main() {
    println!("1. WHILE THE TEXT IS ASCII, THE ROTATION IS ARITHMETIC ON u8");
    println!("   b'h' = {}   b'h' + 13 = {}   as char = {:?}", b'h', b'h' + 13, char::from(b'h' + 13));
    println!("   rot_ascii(\"Hello, World!\", 13) = {:?}", rot_ascii("Hello, World!", 13));
    println!("   Every byte stays inside 0x00..=0x7F, so the String is still valid UTF-8");
    println!("   for free -- no check needed, because ASCII is a subset of UTF-8.");
    println!();

    println!("2. AND IT IS ITS OWN INVERSE");
    let once = rot_ascii("Hello, World!", 13);
    println!("   {:?} -> {:?}", once, rot_ascii(&once, 13));
    println!();

    println!("3. WHAT A ROTATION COSTS IS A METHOD ON THE TYPE: char::len_utf8()");
    for c in ['h', 'u', '\u{2068}', '\u{e9}', '\u{1F600}'] {
        println!(
            "   U+{:04X}  len_utf8 = {}  bytes = {:02x?}",
            c as u32,
            c.len_utf8(),
            c.to_string().as_bytes()
        );
    }
    println!("   'h' rotated by 13 is still one byte. 'h' rotated by 0x2000 is three.");
    println!("   A ciphertext that is three times the size of the plaintext is not a");
    println!("   rotation of the alphabet any more -- it is a re-encoding.");
    println!();

    println!("4. char::from_u32 RETURNS Option, SO THE TYPE REFUSES THE HOLES");
    for n in [0x0068u32, 0x2068, 0xD800, 0xDFFF, 0x10FFFF, 0x110000] {
        match char::from_u32(n) {
            Some(c) => println!("   from_u32(0x{:04X}) = Some(U+{:04X})  len_utf8 {}", n, c as u32, c.len_utf8()),
            None => println!("   from_u32(0x{:04X}) = None", n),
        }
    }
    println!("   Python's chr() hands back a lone surrogate and fails later, at encode time.");
    println!("   Rust cannot build the value at all: there is no char for those numbers.");
    println!();

    println!("5. SO 'ROTATE THE WHOLE TABLE' CANNOT BE ONE SUM");
    let total = 0x110000u32;
    let real = (0..total).filter(|&n| char::from_u32(n).is_some()).count();
    println!("   numbers in the code point range 0..0x110000 : {}", total);
    println!("   of those, numbers that are a char           : {}", real);
    println!("   numbers that are NOT                        : {}", total as usize - real);
    println!("   The gap is U+D800..=U+DFFF, the surrogates, permanently reserved.");
    println!("   Any rotation over Unicode has to carry a list of the code points it may");
    println!("   produce and step over that hole -- and once you are carrying a table,");
    println!("   the 'it is just a sum' selling point of ROT13 is gone.");
}
