// Grouping a slice in Rust: the short last group is a decision, not an accident.
//
// Run:  rustc --edition 2024 grouping_is_a_choice_rs.rs && ./grouping_is_a_choice_rs

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

fn main() {
    let data = "café".as_bytes(); // five bytes, so nothing divides by four
    println!("input: {:?}, {} bytes\n", std::str::from_utf8(data).unwrap(), data.len());

    println!("1. chunks(4) HANDS YOU A SHORT ONE AND SAYS NOTHING");
    for (i, c) in data.chunks(4).enumerate() {
        println!("   chunk {i}: {:<8} {} bytes", hex(c), c.len());
    }
    println!("   Every chunk has type &[u8]. The last one is a different size and the");
    println!("   type cannot say so, which is exactly how a tail gets processed twice");
    println!("   or read past the end.\n");

    println!("2. chunks_exact(4) REFUSES TO GIVE YOU A SHORT ONE");
    let mut groups = data.chunks_exact(4);
    for (i, c) in groups.by_ref().enumerate() {
        println!("   chunk {i}: {:<8} {} bytes", hex(c), c.len());
    }
    println!("   remainder: {:<8} {} bytes", hex(groups.remainder()), groups.remainder().len());
    println!("   The leftover did not vanish; it moved to a method you have to call.");
    println!("   Forgetting it is now visible in the code rather than in the output.\n");

    println!("3. THE FORGETTING, SIDE BY SIDE");
    let all: u32 = data.chunks(4).map(|c| c.len() as u32).sum();
    let exact: u32 = data.chunks_exact(4).map(|c| c.len() as u32).sum();
    println!("   bytes seen via chunks(4)        {all}  (all of them)");
    println!("   bytes seen via chunks_exact(4)  {exact}  (one short of the file)");
    println!("   Same loop, same width, one byte of café silently missing.\n");

    println!("4. THERE IS NO BIT-LEVEL CHUNKER, AND THAT IS HONEST");
    println!("   std groups &[u8]: the smallest thing it can hand you is one byte.");
    println!("   A 5-bit group (Base32) or a 6-bit group (Base64) is not a subslice of");
    println!("   anything, so you shift it out yourself:");
    let mut acc: u32 = 0;
    let mut nbits: u32 = 0;
    let mut sixes = Vec::new();
    for &b in data {
        acc = (acc << 8) | u32::from(b);
        nbits += 8;
        while nbits >= 6 {
            nbits -= 6;
            sixes.push((acc >> nbits) & 0b11_1111);
        }
    }
    if nbits > 0 {
        sixes.push((acc << (6 - nbits)) & 0b11_1111); // the ragged tail, zero-filled
    }
    println!("   six-bit groups: {sixes:?}");
    println!("   Note the last one had to be filled out to six bits to exist at all.");
    println!("   That fill is what Base64's '=' is there to declare.");
}
