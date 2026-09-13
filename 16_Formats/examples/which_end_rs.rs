//! The byte order is a value, not a type: three headers from the chapter,
//! and the read that has to pick from_le_bytes or from_be_bytes at run time.
//!
//! Build:  rustc --edition 2024 which_end_rs.rs && ./which_end_rs

fn u16_at(b: &[u8], at: usize, little: bool) -> u16 {
    let pair = [b[at], b[at + 1]];
    if little { u16::from_le_bytes(pair) } else { u16::from_be_bytes(pair) }
}

fn u32_at(b: &[u8], at: usize, little: bool) -> u32 {
    let quad = [b[at], b[at + 1], b[at + 2], b[at + 3]];
    if little { u32::from_le_bytes(quad) } else { u32::from_be_bytes(quad) }
}

fn hex(b: &[u8]) -> String {
    b.iter().map(|x| format!("{x:02x}")).collect::<Vec<_>>().join(" ")
}

fn section(n: u8, title: &str) {
    println!("{n}. {title}");
    println!("{}", "-".repeat(72));
}

fn main() {
    section(1, "ELF: BYTE 5 SAYS WHICH FUNCTION TO CALL");
    // Two ELF headers with the same e_type (2, EXEC) and e_machine (0x3e, x86-64):
    // one little-endian 64-bit, one big-endian 32-bit. Only e_ident differs in
    // kind; the numbers after it are laid out in the order byte 5 names.
    let lsb: [u8; 20] = [0x7f, b'E', b'L', b'F', 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x02, 0x00, 0x3e, 0x00];
    let msb: [u8; 20] = [0x7f, b'E', b'L', b'F', 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x00, 0x02, 0x00, 0x3e];
    for (label, ident) in [("LSB, 64-bit", &lsb), ("MSB, 32-bit", &msb)] {
        let little = ident[5] == 1;
        let width = if ident[4] == 2 { 64 } else { 32 };
        let e_type = u16_at(ident, 16, little);
        let e_machine = u16_at(ident, 18, little);
        println!("   {label:<12} bytes 16..20  {}   byte 5 = {} -> {}",
            hex(&ident[16..20]), ident[5], if little { "from_le_bytes" } else { "from_be_bytes" });
        println!("                e_type {e_type}  e_machine {e_machine:#x}  header will be {} bytes",
            if width == 64 { 64 } else { 52 });
    }
    println!();
    println!("   Same two numbers out of two different byte layouts, because the");
    println!("   file said which layout it used. Read the MSB file as if it were");
    println!("   LSB and e_type is {} -- a number, not an error.", u16_at(&msb, 16, true));
    println!();

    section(2, "MACH-O: THE MAGIC'S SPELLING SAYS IT");
    // 0xfeedfacf written by a little-endian machine, then by a big-endian one.
    let on_x86: [u8; 4] = 0xfeedfacf_u32.to_le_bytes();
    let on_ppc: [u8; 4] = 0xfeedfacf_u32.to_be_bytes();
    for (label, b) in [("written little-endian", &on_x86), ("written big-endian", &on_ppc)] {
        let as_le = u32_at(b, 0, true);
        let verdict = match as_le {
            0xfeedface => "MH_MAGIC     32-bit, same order as this reader",
            0xfeedfacf => "MH_MAGIC_64  64-bit, same order as this reader",
            0xcefaedfe => "MH_CIGAM     32-bit, the other order",
            0xcffaedfe => "MH_CIGAM_64  64-bit, the other order",
            _ => "not Mach-O",
        };
        println!("   {label:<24} {}   read LE {as_le:#010x}   {verdict}", hex(b));
    }
    println!();
    println!("   Ghidra reads the four bytes little-endian and accepts all four");
    println!("   values; which one it met is what tells it the file's order.");
    println!();

    section(3, "TWO BYTES, TWO NUMBERS");
    let mz: [u8; 2] = *b"MZ";
    let di: [u8; 2] = *b"DI";
    println!("   {}  'MZ'   little {:#06x}   big {:#06x}", hex(&mz), u16_at(&mz, 0, true), u16_at(&mz, 0, false));
    println!("   {}  'DI'   little {:#06x}   big {:#06x}", hex(&di), u16_at(&di, 0, true), u16_at(&di, 0, false));
    println!();
    println!("   A two-byte text signature is one picture and two numbers, and a");
    println!("   constant in a program has to be one of them. Ghidra's DOS header");
    println!("   compares against 0x5a4d; its DBG header keeps both.");
    println!();

    section(4, "CAFEBABE: THE NEXT FOUR BYTES SETTLE IT");
    let fat = [0xca, 0xfe, 0xba, 0xbe, 0, 0, 0, 2];
    let class = [0xca, 0xfe, 0xba, 0xbe, 0, 0, 0, 0x45];
    for (label, b) in [("a fat Mach-O, 2 slices", &fat), ("a Java class, version 69", &class)] {
        let n = u32_at(b, 4, false);
        println!("   {label:<26} {}   u32 at 4 = {n:<4} {}", hex(b),
            if n > 30 { "> 30: a class file" } else { "<= 30: a slice count" });
    }
    println!();
    println!("   Both are big-endian at offset 4, so the reader needs no choice");
    println!("   here -- only a threshold, which is the one file(1) uses.");
}
