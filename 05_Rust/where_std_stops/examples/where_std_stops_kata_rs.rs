// Kata answers for Where std stops.
//
// Six jobs. For each one the question is whether std can FINISH it, and the
// answer key is what std actually returns.
//
// Build & run:  rustc --edition 2024 where_std_stops_kata_rs.rs && ./where_std_stops_kata_rs

fn main() {
    println!("1. b\"caf\\xe9\" is Latin-1; decode it");
    let s: String = b"caf\xe9".iter().map(|&b| b as char).collect();
    println!("   bytes.iter().map(|&b| b as char).collect() -> {s:?}");
    println!("   YES, std, one line -- because Latin-1 is the first 256 code points.");
    println!();

    println!("2. The same four bytes are windows-1250; decode them");
    let s: String = b"caf\xe9".iter().map(|&b| b as char).collect();
    println!("   the same line gives {s:?}, and it is right only because e9 is é in both tables.");
    let bf: String = b"\xbf".iter().map(|&b| b as char).collect();
    println!("   on b\"\\xbf\" it gives {bf:?}; windows-1250 says ż");
    println!("   NO -- a 128-entry table you do not have. encoding_rs.");
    println!();

    println!("3. Count what a user sees in the family emoji");
    let family = "👨\u{200d}👩\u{200d}👧\u{200d}👦";
    println!("   len() {}   chars().count() {}   encode_utf16().count() {}   a user sees 1", family.len(), family.chars().count(), family.encode_utf16().count());
    println!("   NO -- three rulers, and none of them is that one. unicode-segmentation.");
    println!();

    println!("4. Is \"café\" the same word as \"cafe\" + U+0301?");
    println!("   == -> {}", "café" == "cafe\u{301}");
    println!("   NO -- std has no normalization. unicode-normalization, or icu.");
    println!();

    println!("5. Find the first byte of a file that is not UTF-8");
    let owned: Vec<u8> = b"caf\xe9 au lait".to_vec();
    let b: &[u8] = &owned;
    println!("   from_utf8(b).unwrap_err().valid_up_to() -> {}", std::str::from_utf8(b).unwrap_err().valid_up_to());
    println!("   YES, std -- and it is the same number simdutf8::compat reports, byte for byte.");
    println!();

    println!("6. Sort [\"łódź\", \"lód\", \"zebra\"] the way a Polish dictionary does");
    let mut w = vec!["łódź", "lód", "zebra"];
    w.sort();
    println!("   sort() -> {w:?}");
    println!("   NO -- code point order puts ł after z. icu::collator with locale pl: lód, łódź, zebra.");
    println!();

    println!("Score: 2 of 6 std finishes, 4 need a crate -- and both YES rows are the ones");
    println!("where the answer is arithmetic on bytes rather than a table.");
}
