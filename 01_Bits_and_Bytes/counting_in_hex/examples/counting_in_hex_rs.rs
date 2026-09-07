// Counting in hex, in a type that has a width: where the wheels are, and where they stop.
//
// Run:  rustc --edition 2024 counting_in_hex_rs.rs -o /tmp/counting && /tmp/counting

fn main() {
    let n: u8 = 33;

    println!("1. THE TWO HALVES OF A BYTE ARE A SHIFT AND A MASK");
    println!("   n = {n} = 0x{n:02X} = 0b{n:08b}");
    println!("   high nibble   n >> 4     = {:X}   the 16s digit", n >> 4);
    println!("   low nibble    n & 0x0F   = {:X}   the 1s digit", n & 0x0F);
    println!("   and back      (hi << 4) | lo = {}", ((n >> 4) << 4) | (n & 0x0F));
    println!("   Those two digits are what a hex dump prints. Nothing is computed to get them;");
    println!("   the byte was already two hex digits, and the shift only picks which one you want.");
    println!();

    println!("2. std WILL NAME THE SIGNIFICANT BIT, BECAUSE IT IS A POSITION AND NOT A VALUE");
    for v in [1u8, 33, 128, 255] {
        let hi = 7 - v.leading_zeros(); // index of the highest bit that is set
        println!(
            "   0x{v:02X} = 0b{v:08b}   leading_zeros {}   highest set bit is bit {hi} (worth {})   ones {}   trailing_zeros {}",
            v.leading_zeros(),
            1u32 << hi,
            v.count_ones(),
            v.trailing_zeros(),
        );
    }
    println!("   Bit 7 is the most significant bit of a u8 whatever is in it -- 33 has a 0 there and");
    println!("   it is still the most significant bit. `leading_zeros` reports the highest bit that is SET,");
    println!("   which is a different question and the one you usually want.");
    println!();

    println!("3. FF + 1 IN A BYTE: FOUR ANSWERS, AND THE TYPE MAKES YOU PICK ONE");
    let max = u8::MAX;
    println!("   u8::MAX                     = {max} = 0x{max:02X}");
    println!("   max.checked_add(1)          = {:<9}  there is no answer, and the type says so", format!("{:?}", max.checked_add(1)));
    println!("   max.wrapping_add(1)         = {:<9}  the carry is discarded: the odometer rolls to 00", max.wrapping_add(1));
    println!("   max.overflowing_add(1)      = {:<9}  the answer, and the fact that it overflowed", format!("{:?}", max.overflowing_add(1)));
    println!("   max.saturating_add(1)       = {:<9}  stop at the top rather than roll round to it", max.saturating_add(1));
    println!("   Plain `max + 1` is a fifth: it panics in a debug build and wraps in a release one, so it");
    println!("   is the only one of the five whose meaning depends on how the program was compiled.");
    println!("   Written as a literal it does not even compile -- `arithmetic_overflow` is deny-by-default.");
    println!();

    println!("4. AND 'MSB' MEANS TWO DIFFERENT THINGS, ONE BIT APART FROM ONE BYTE");
    let w: u16 = 0x02A5;
    println!("   w = 0x{w:04X} = {w}");
    println!("   most significant BIT   w >> 15        = {}          one bit, the 32768s column", w >> 15);
    println!("   most significant BYTE  (w >> 8) as u8 = 0x{:02X}       one byte, the 256s column", (w >> 8) as u8);
    println!("   w.to_be_bytes()  = {:02X?}   big-endian:    most significant byte written first", w.to_be_bytes());
    println!("   w.to_le_bytes()  = {:02X?}   little-endian: least significant byte written first", w.to_le_bytes());
    println!("   Same number, same significance, two orders on disk. Which is why 'the MSB' is only ever");
    println!("   clear from context: in a bit-twiddling sentence it is one bit, in a byte-order sentence");
    println!("   it is one byte, and the abbreviation is identical for both.");
}
