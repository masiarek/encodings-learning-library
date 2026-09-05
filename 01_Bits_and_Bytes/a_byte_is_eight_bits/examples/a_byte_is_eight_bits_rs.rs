// A byte is eight switches. Rust's name for one is `u8`.
//
// Build & run:  rustc --edition 2024 a_byte_is_eight_bits_rs.rs && ./a_byte_is_eight_bits_rs

fn main() {
    let b: u8 = 65;

    println!("1. ONE VALUE, THREE SPELLINGS");
    println!("   decimal  {b}");
    println!("   binary   {b:08b}      ({{:08b}} pads to eight digits)");
    println!("   as text  {}           ({{as char}} reads the same byte as ASCII)", b as char);
    println!();

    println!("2. THE WIDTH IS PART OF THE TYPE");
    println!("   size_of::<u8>()  = {} byte", size_of::<u8>());
    println!("   u8::MIN ..= u8::MAX = {} ..= {}", u8::MIN, u8::MAX);
    println!("   255u8.checked_add(1) = {:?}   (a ninth bit does not exist)", 255u8.checked_add(1));
    println!("   255u8.wrapping_add(1) = {}      (asked to wrap, it wraps)", 255u8.wrapping_add(1));
    println!();

    println!("3. BINARY LITERALS AND PARSING");
    let from_literal: u8 = 0b0100_0001;
    let from_text = u8::from_str_radix("01000001", 2).unwrap();
    println!("   0b0100_0001                          = {from_literal}");
    println!("   u8::from_str_radix(\"01000001\", 2)  = {from_text}");
    println!();

    println!("4. EVERY PLACE VALUE, READ OFF THE BITS OF 200");
    let n: u8 = 200;
    let mut terms = Vec::new();
    for shift in (0..8).rev() {
        let bit = (n >> shift) & 1;
        if bit == 1 {
            terms.push((1u16 << shift).to_string());
        }
    }
    println!("   {n} = {n:08b} = {}", terms.join(" + "));
}
