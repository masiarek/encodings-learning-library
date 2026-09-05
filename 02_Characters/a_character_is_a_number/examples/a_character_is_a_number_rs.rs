// ASCII in Rust: a `u8` that happens to be a letter, and the `is_ascii_*` family.
//
// Build & run:  rustc --edition 2024 a_character_is_a_number_rs.rs && ./a_character_is_a_number_rs

fn main() {
    println!("1. b'A' IS A u8. 'A' IS A char. THEY AGREE ON THE NUMBER.");
    let byte: u8 = b'A';
    let ch: char = 'A';
    println!("   b'A' = {byte}   'A' as u32 = {}   equal: {}", ch as u32, byte as u32 == ch as u32);
    println!("   65u8 as char = {:?}   char::from(65u8) = {:?}", 65u8 as char, char::from(65u8));
    println!();

    println!("2. THE LAYOUT TRICKS, IN BYTE ARITHMETIC");
    println!("   b'7' - b'0'        = {}", b'7' - b'0');
    println!("   (b'a' ^ 0x20) as char = {:?}", (b'a' ^ 0x20) as char);
    println!("   b'q'.to_ascii_uppercase() = {:?}   (std does the same bit flip, safely)", b'q'.to_ascii_uppercase() as char);
    println!();

    println!("3. std CAN ASK EVERY QUESTION ABOUT THE TABLE");
    for b in [b'A', b'a', b'7', b' ', b'\n', 0xC3u8] {
        println!(
            "   {:>4}  0x{b:02X}  ascii={:<5} alpha={:<5} digit={:<5} ctrl={:<5} upper={}",
            format!("{:?}", b as char),
            b.is_ascii(),
            b.is_ascii_alphabetic(),
            b.is_ascii_digit(),
            b.is_ascii_control(),
            b.is_ascii_uppercase(),
        );
    }
    println!("   0xC3 is not ASCII: the top bit is set. `as char` still gives SOMETHING — see the note on the page.");
    println!();

    println!("4. A BYTE STRING IS ASCII WHEN EVERY BYTE IS");
    println!("   b\"Hi there\".is_ascii() = {}", b"Hi there".is_ascii());
    println!("   \"caf\\u{{e9}}\".is_ascii()   = {}", "caf\u{e9}".is_ascii());
}
