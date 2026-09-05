// A code page is 128 numbers you have to ship. Except one.
//
// Rust's std has exactly one decoder, for UTF-8, and no code pages at all --
// so writing one here is the shortest way to see what a code page IS when the
// romance is stripped off: an array. Latin-1 is the exception, and the reason
// it is the exception is the whole point of this file.
//
// Build:  rustc --edition 2024 code_pages_rs.rs -o /tmp/cp && /tmp/cp
//
// CP1250_TOP below was typed by hand and then machine-diffed, entry by entry,
// against Python's own `cp1250` codec -- all 128 match, and the five undefined
// slots land in the same places. Redo that check with:
//
//   python3 -c "import re,sys; src=open('code_pages_rs.rs').read(); \
//     b=src[src.index('const CP1250_TOP'):]; b=b[:b.index('];')]; \
//     mine=[int(x,16) for x in re.findall(r'\\u\{([0-9A-Fa-f]+)\}', b)]; \
//     real=[(lambda d: ord(d) if d else 0xFFFD)(bytes([n]).decode('cp1250','ignore')) \
//           for n in range(0x80,0x100)]; print('match' if mine==real else 'DIFFERS')"

fn head(n: u32, title: &str) {
    println!("\n{n}. {title}\n{}", "-".repeat(72));
}

/// Latin-1's top half. No data: the byte IS the code point.
fn latin1(byte: u8) -> char {
    byte as char
}

/// Windows-1250's top half, 0x80..=0xFF -- the actual numbers, because there
/// is no rule to compute them from. '\u{FFFD}' marks the five undefined slots.
const CP1250_TOP: [char; 128] = [
    '\u{20AC}', '\u{FFFD}', '\u{201A}', '\u{FFFD}', '\u{201E}', '\u{2026}', '\u{2020}', '\u{2021}',
    '\u{FFFD}', '\u{2030}', '\u{0160}', '\u{2039}', '\u{015A}', '\u{0164}', '\u{017D}', '\u{0179}',
    '\u{FFFD}', '\u{2018}', '\u{2019}', '\u{201C}', '\u{201D}', '\u{2022}', '\u{2013}', '\u{2014}',
    '\u{FFFD}', '\u{2122}', '\u{0161}', '\u{203A}', '\u{015B}', '\u{0165}', '\u{017E}', '\u{017A}',
    '\u{00A0}', '\u{02C7}', '\u{02D8}', '\u{0141}', '\u{00A4}', '\u{0104}', '\u{00A6}', '\u{00A7}',
    '\u{00A8}', '\u{00A9}', '\u{015E}', '\u{00AB}', '\u{00AC}', '\u{00AD}', '\u{00AE}', '\u{017B}',
    '\u{00B0}', '\u{00B1}', '\u{02DB}', '\u{0142}', '\u{00B4}', '\u{00B5}', '\u{00B6}', '\u{00B7}',
    '\u{00B8}', '\u{0105}', '\u{015F}', '\u{00BB}', '\u{013D}', '\u{02DD}', '\u{013E}', '\u{017C}',
    '\u{0154}', '\u{00C1}', '\u{00C2}', '\u{0102}', '\u{00C4}', '\u{0139}', '\u{0106}', '\u{00C7}',
    '\u{010C}', '\u{00C9}', '\u{0118}', '\u{00CB}', '\u{011A}', '\u{00CD}', '\u{00CE}', '\u{010E}',
    '\u{0110}', '\u{0143}', '\u{0147}', '\u{00D3}', '\u{00D4}', '\u{0150}', '\u{00D6}', '\u{00D7}',
    '\u{0158}', '\u{016E}', '\u{00DA}', '\u{0170}', '\u{00DC}', '\u{00DD}', '\u{0162}', '\u{00DF}',
    '\u{0155}', '\u{00E1}', '\u{00E2}', '\u{0103}', '\u{00E4}', '\u{013A}', '\u{0107}', '\u{00E7}',
    '\u{010D}', '\u{00E9}', '\u{0119}', '\u{00EB}', '\u{011B}', '\u{00ED}', '\u{00EE}', '\u{010F}',
    '\u{0111}', '\u{0144}', '\u{0148}', '\u{00F3}', '\u{00F4}', '\u{0151}', '\u{00F6}', '\u{00F7}',
    '\u{0159}', '\u{016F}', '\u{00FA}', '\u{0171}', '\u{00FC}', '\u{00FD}', '\u{0163}', '\u{02D9}',
];

fn cp1250(byte: u8) -> char {
    if byte < 0x80 { byte as char } else { CP1250_TOP[(byte - 0x80) as usize] }
}

fn main() {
    // -------------------------------------------------------------- 1
    head(1, "A CODE PAGE, AS A DATA STRUCTURE");
    println!("   fn latin1(b: u8) -> char {{ b as char }}                 <- no data");
    println!("   const CP1250_TOP: [char; 128] = [ ... ];              <- 128 numbers");
    println!();
    println!("   That asymmetry is the lesson. Latin-1 needs no table because it");
    println!("   IS the identity: byte value equals code point, all the way to 255.");
    println!("   Every other code page is a list somebody has to ship, and a list");
    println!("   is a thing you can be given the wrong copy of.");

    // -------------------------------------------------------------- 2
    head(2, "THE SAME BYTES, THROUGH BOTH FUNCTIONS");
    let lodz = [0xA3u8, 0xF3, 0x64, 0x9F]; // "Łódź" as CP1250
    println!("   bytes {lodz:02x?}");
    println!("     latin1  -> {:?}", lodz.iter().map(|&b| latin1(b)).collect::<String>());
    println!("     cp1250  -> {:?}", lodz.iter().map(|&b| cp1250(b)).collect::<String>());
    println!();
    println!("   One of those is a Polish city and one is a pound sign and some");
    println!("   punctuation. Both functions ran without complaint, because");
    println!("   neither one has anything to complain about: a lookup cannot fail.");

    // -------------------------------------------------------------- 3
    head(3, "WHERE THE TWO TABLES AGREE, AND WHERE THEY DO NOT");
    let agree = (0x80..=0xFFu8).filter(|&b| latin1(b) == cp1250(b)).count();
    let holes = (0x80..=0xFFu8).filter(|&b| cp1250(b) == '\u{FFFD}').count();
    println!("   of the 128 bytes 0x80-0xFF:");
    println!("     the two tables agree on   {agree}");
    println!("     CP1250 defines nothing at {holes}");
    println!();
    println!("   twelve of the disagreements, from 0xA0 up where both tables");
    println!("   have real letters rather than control codes:");
    for (i, b) in (0xA0..=0xFFu8).filter(|&b| latin1(b) != cp1250(b)).take(12).enumerate() {
        if i % 4 == 0 { print!("\n    "); }
        print!(" {b:#04x} {} vs {}", latin1(b), cp1250(b));
    }
    println!("\n");
    println!("   Rust ships none of this. std has one decoder -- UTF-8 -- and for");
    println!("   anything else you reach for a crate (`encoding_rs`), which is");
    println!("   itself a statement: in 2026 a code page is a compatibility");
    println!("   concern, not a way to write files.");
}
