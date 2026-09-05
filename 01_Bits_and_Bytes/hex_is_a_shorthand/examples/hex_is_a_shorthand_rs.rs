// Hex is binary written four bits at a time. Rust has a spelling for each.
//
// Build & run:  rustc --edition 2024 hex_is_a_shorthand_rs.rs && ./hex_is_a_shorthand_rs

fn main() {
    let b: u8 = 65;

    println!("1. FOUR FORMAT SPECIFIERS, ONE VALUE");
    println!("   {{:x}}     -> {b:x}       lowercase hex, no padding");
    println!("   {{:02X}}   -> {b:02X}       uppercase, two digits — the byte-shaped one");
    println!("   {{:#04x}}  -> {b:#04x}     prefix included, width counts the prefix");
    println!("   {{:08b}}   -> {b:08b} the same eight bits, one per digit");
    println!();

    println!("2. THREE LITERALS THAT ARE ALL 65");
    let hex: u8 = 0x41;
    let bin: u8 = 0b0100_0001;
    let chr: u8 = b'A';
    println!("   0x41 == 0b0100_0001 == b'A'  ->  {}", hex == bin && bin == chr);
    println!();

    println!("3. PARSING NEEDS THE BASE, AND REFUSES THE PREFIX");
    println!("   u8::from_str_radix(\"41\", 16)   -> {:?}", u8::from_str_radix("41", 16));
    println!("   u8::from_str_radix(\"0x41\", 16) -> {:?}", u8::from_str_radix("0x41", 16));
    println!("   (the prefix is for humans; the parser wants digits only)");
    println!();

    println!("4. A BYTE STRING PRINTED AS HEX, TWO DIGITS PER BYTE");
    let word = b"caf\xc3\xa9";
    let dump: Vec<String> = word.iter().map(|x| format!("{x:02x}")).collect();
    println!("   {:?} -> {}", "café", dump.join(" "));
    println!("   five bytes for four letters; the last two are the é. Next chapter.");
}
