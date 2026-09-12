//! The dialog's twenty operations as Rust, one line each.
//!
//! 010 Editor's manual writes every hex operation in C notation and does not
//! say what happens when a result will not fit. Rust's integer types will not
//! leave that unsaid: the same line has to be written wrapping_, checked_ or
//! saturating_, and the name of the method is the answer.
//!
//! Run:  rustc --edition 2024 hex_operations_rs.rs && ./hex_operations_rs

fn bytes(v: &[u8]) -> String {
    v.iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" ")
}

fn option(v: Option<u8>) -> String {
    match v {
        Some(b) => format!("Some(0x{b:02x})"),
        None => "None".to_string(),
    }
}

fn main() {
    println!("1. THE TWENTY, ON ONE BYTE");
    println!("{}", "-".repeat(72));
    println!("   x is 0xf0u8, which is 240; s is the same bits as an i8, -16.");
    println!("   Treat Data As is the type, and the dialog's formula is the line.");
    println!();
    let x: u8 = 0xf0;
    let s: i8 = x as i8;
    let rows: [(&str, &str, u8); 20] = [
        ("Assign 0x41", "0x41", 0x41),
        ("Add 0x20", "x.wrapping_add(0x20)", x.wrapping_add(0x20)),
        ("Subtract 0xf1", "x.wrapping_sub(0xf1)", x.wrapping_sub(0xf1)),
        ("Multiply 3", "x.wrapping_mul(3)", x.wrapping_mul(3)),
        ("Divide 3", "x / 3", x / 3),
        ("Divide 3, Signed", "s / 3", (s / 3) as u8),
        ("Negate", "x.wrapping_neg()", x.wrapping_neg()),
        ("Modulus 7", "x % 7", x % 7),
        ("Modulus 7, Signed", "s % 7", (s % 7) as u8),
        ("Set Minimum 0xf8", "x.max(0xf8)", x.max(0xf8)),
        ("Set Maximum 0x7f", "x.min(0x7f)", x.min(0x7f)),
        ("Binary And 0x3c", "x & 0x3c", x & 0x3c),
        ("Binary Or 0x0f", "x | 0x0f", x | 0x0f),
        ("Binary Xor 0xff", "x ^ 0xff", x ^ 0xff),
        ("Binary Invert", "!x", !x),
        ("Shift Left 1", "x << 1", x << 1),
        ("Shift Right 1", "x >> 1", x >> 1),
        ("Shift Right 1, Signed", "s >> 1", (s >> 1) as u8),
        ("Rotate Left 4", "x.rotate_left(4)", x.rotate_left(4)),
        ("Rotate Right 1", "x.rotate_right(1)", x.rotate_right(1)),
    ];
    for (operation, rust, result) in rows {
        println!("     {operation:<24} {rust:<24} {result:02x}");
    }
    println!();
    println!("   The two that do not fit in one byte:");
    println!();
    let short = u16::from_le_bytes([0x34, 0x12]);
    println!(
        "     {:<24} {:<24} {}",
        "Swap Bytes, Short",
        "v.swap_bytes()",
        bytes(&short.swap_bytes().to_le_bytes())
    );
    let block = u32::from_be_bytes([0x12, 0x34, 0x56, 0x78]);
    println!(
        "     {:<24} {:<24} {}",
        "Block Shift Left 4",
        "v << 4, as one u32",
        bytes(&(block << 4).to_be_bytes())
    );
    println!(
        "     {:<24} {:<24} {}",
        "Block Shift Right 4",
        "v >> 4, as one u32",
        bytes(&(block >> 4).to_be_bytes())
    );
    println!("     (Swap Bytes starts from 34 12; the Block Shifts from 12 34 56 78.)");
    println!();

    println!("2. WHAT THE C NOTATION DOES NOT SAY, RUST MAKES YOU SAY");
    println!("{}", "-".repeat(72));
    println!("   Each group is one question the manual leaves open, and each line one");
    println!("   answer Rust will let you choose.");
    println!();
    row("0xf0u8.wrapping_add(0x20)", format!("0x{:02x}", 0xf0u8.wrapping_add(0x20)), "a result that does not fit");
    row("0xf0u8.checked_add(0x20)", option(0xf0u8.checked_add(0x20)), "");
    row("0xf0u8.saturating_add(0x20)", format!("0x{:02x}", 0xf0u8.saturating_add(0x20)), "");
    println!();
    row("i8::MIN.wrapping_neg()", i8::MIN.wrapping_neg().to_string(), "the value with no positive twin");
    row("i8::MIN.checked_neg()", format!("{:?}", i8::MIN.checked_neg()), "");
    println!();
    row("0x10u8.checked_div(0)", option(0x10u8.checked_div(0)), "dividing by zero");
    println!();
    row("-7i8 / 2", (-7i8 / 2).to_string(), "a negative quotient");
    row("(-7i8).div_euclid(2)", (-7i8).div_euclid(2).to_string(), "");
    row("-7i8 % 3", (-7i8 % 3).to_string(), "a negative remainder");
    row("(-7i8).rem_euclid(3)", (-7i8).rem_euclid(3).to_string(), "");
    println!();
    row("0x81u8.wrapping_shl(9)", format!("0x{:02x}", 0x81u8.wrapping_shl(9)), "a shift of the width or more");
    row("0x81u8.checked_shl(9)", option(0x81u8.checked_shl(9)), "");
    row("0x81u8.rotate_left(9)", format!("0x{:02x}", 0x81u8.rotate_left(9)), "");
    println!();
    row("0x1234u16.rotate_left(8)", format!("0x{:04x}", 0x1234u16.rotate_left(8)), "a rotation that is a byte swap");
    row("0x1234u16.swap_bytes()", format!("0x{:04x}", 0x1234u16.swap_bytes()), "");
}

fn row(expression: &str, value: String, note: &str) {
    if note.is_empty() {
        println!("     {expression:<30} {value}");
    } else {
        println!("     {expression:<30} {value:<12} {note}");
    }
}
