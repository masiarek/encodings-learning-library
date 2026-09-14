//! Entropy is a histogram, and a histogram is an array of 256 counts indexed by
//! the byte: the type says every u8 has a bucket. Then Ghidra's own integer
//! arithmetic -- the palette index it stores for a score, the number its tooltip
//! prints back, and the bands its seven named ranges become -- reproduced from
//! the 12.1.3 source, so the page's tables come from a program and not a reading.
//!
//! Build:  rustc --edition 2024 entropy_bar_rs.rs && ./entropy_bar_rs

fn histogram(bytes: &[u8]) -> [u32; 256] {
    let mut h = [0u32; 256];
    for &b in bytes {
        h[b as usize] += 1; // a u8 is 0..=255, so this index cannot miss and needs no offset
    }
    h
}

fn entropy(bytes: &[u8]) -> f64 {
    let n = bytes.len() as f64;
    histogram(bytes)
        .iter()
        .filter(|&&c| c > 0)
        .map(|&c| {
            let p = c as f64 / n;
            -p * p.log2()
        })
        .sum()
}

fn values_in_use(bytes: &[u8]) -> usize {
    histogram(bytes).iter().filter(|&&c| c > 0).count()
}

fn utf16le(s: &str) -> Vec<u8> {
    s.encode_utf16().flat_map(|u| u.to_le_bytes()).collect()
}

/// EntropyOverviewColorService.quantizeChunk: floor(score / 8 * 256), capped at 255.
fn palette_index(score: f64) -> usize {
    ((score / 8.0 * 256.0).floor() as usize).min(255)
}

/// EntropyOverviewColorService.getToolTipText: index * 8 / 255, shown with the format #0.0.
fn tooltip(index: usize) -> f64 {
    index as f64 * 8.0 / 255.0
}

struct Knot {
    label: &'static str,
    name: &'static str,
    centre: f64,
    width: f64,
}

// EntropyKnot.java, Ghidra 12.1.3, in the enum's order.
const KNOTS: [Knot; 7] = [
    Knot { label: "x86 code", name: "x86", centre: 5.94, width: 0.4 },
    Knot { label: "ARM code", name: "arm", centre: 5.1252, width: 0.51 },
    Knot { label: "THUMB code", name: "thumb", centre: 6.2953, width: 0.5 },
    Knot { label: "PowerPC code", name: "powerpc", centre: 5.6674, width: 0.52 },
    Knot { label: "ASCII strings", name: "ascii", centre: 4.7, width: 0.5 },
    Knot { label: "Compressed", name: "compressed", centre: 8.0, width: 0.5 },
    Knot { label: "Unicode UTF16", name: "utf16", centre: 3.21, width: 0.2 },
];

/// The palette indexes a knot claims, both ends inclusive.
/// EntropyOverviewOptionsManager.addPaletteKnot floors the centre and the
/// half-width onto the 256-entry palette and clamps the centre to 255;
/// OverviewPalette.addKnot mirrors the start about the centre for the end and
/// clamps that to 256; KnotRecord.contains is start <= i && i <= end.
fn band(k: &Knot) -> (usize, usize) {
    let point = ((32.0 * k.centre).floor() as usize).min(255);
    let half = (32.0 * k.width).floor() as usize;
    let start = point.saturating_sub(half);
    let end = (2 * (point - start) + 1 + start).min(256);
    (start, end)
}

fn section(n: u8, title: &str) {
    println!("{n}. {title}");
    println!("{}", "-".repeat(72));
}

fn main() {
    section(1, "A HISTOGRAM IS 256 COUNTS, INDEXED BY THE BYTE");
    println!("   {:<16} {:<9} {:>5} {:>6}   {:>5}   log2(values)", "string", "encoding", "bytes", "values", "score");
    for s in ["Hello, World!", "café", "żółw", "日本語", "😀"] {
        for (enc, bytes) in [("UTF-8", s.as_bytes().to_vec()), ("UTF-16LE", utf16le(s))] {
            let v = values_in_use(&bytes);
            println!(
                "   {:<16} {:<9} {:>5} {:>6}   {:5.2}   {:12.2}",
                s, enc, bytes.len(), v, entropy(&bytes), (v as f64).log2()
            );
        }
    }
    println!();
    println!("   [0u32; 256] indexed by b as usize: the type is the whole guarantee that");
    println!("   every byte has a bucket. Ghidra is Java, whose byte is signed, so its");
    println!("   histogram is indexed 128 + b -- the same 256 buckets, shifted, and the");
    println!("   sum does not care which bucket is which. When every byte is distinct");
    println!("   the score IS log2 of the count, which is why café is 2.32 in UTF-8");
    println!("   and 2.00 in Latin-1: the ceiling is the number of values in use.");
    println!();

    section(2, "ONE NUMBER FROM 0.0 TO 8.0 BECOMES ONE OF 256 COLOURS");
    println!("   {:>5}   floor(score x 32)   tooltip prints   difference", "score");
    for score in [0.0, 1.0, 3.21, 4.7, 5.94, 7.99, 8.0] {
        let i = palette_index(score);
        println!("   {:5.2}   {:>17}   {:14.4}   {:+.4}", score, i, tooltip(i), tooltip(i) - score);
    }
    println!();
    println!("   The palette has 256 entries, so a score is floored to a step of 1/32");
    println!("   before it is a colour, and a chunk of exactly 8.0 has to be capped");
    println!("   at entry 255. The tooltip turns the entry back into a number by");
    println!("   dividing by 255 -- 256 steps in, 255 steps out -- so every score");
    println!("   above zero comes back a little high. #0.0 rounds most of that away.");
    println!();

    section(3, "THE SEVEN NAMED RANGES ARE INTEGER BANDS");
    println!(
        "   {:<14} {:<11} {:>6} {:>5}   {:<12}   {:>9}   {}",
        "option", "tooltip", "centre", "+/-", "as written", "indexes", "as applied"
    );
    for k in &KNOTS {
        let (s, e) = band(k);
        println!(
            "   {:<14} {:<11} {:>6.4} {:>5.2}   {:4.2} to {:4.2}   {:>3} to {:>3}   {:4.2} to {:4.2}",
            k.label, k.name, k.centre, k.width,
            k.centre - k.width, k.centre + k.width,
            s, e, s as f64 / 32.0, (e + 1) as f64 / 32.0
        );
    }
    println!();
    println!("   Every band is a little wider than its centre plus or minus its");
    println!("   half-width says, because both are floored to 1/32 before the end is");
    println!("   mirrored from the start. Compressed's centre of 8.0 is the one that");
    println!("   hits the cap: entry 256 does not exist, so it is pinned to 255 and the");
    println!("   band is 17 entries below it and none above.");
    println!();
    println!("   Ranges that overlap, so a score inside both is named by the lower slot:");
    for (a, ka) in KNOTS.iter().enumerate() {
        for kb in KNOTS.iter().skip(a + 1) {
            let (sa, ea) = band(ka);
            let (sb, eb) = band(kb);
            if sa <= eb && sb <= ea {
                let lo = sa.max(sb);
                let hi = ea.min(eb);
                println!("   {:<8} and {:<8}   share entries {:>3} to {:>3}   ({:4.2} to {:4.2})",
                    ka.name, kb.name, lo, hi, lo as f64 / 32.0, (hi + 1) as f64 / 32.0);
            }
        }
    }
    println!();
    println!("   The four machine-code ranges are one region of the scale, 4.6 to 6.8,");
    println!("   sliced four ways; x86 lies wholly inside PowerPC's and THUMB's");
    println!("   overlap. Which name the tooltip prints for a score in two of them");
    println!("   is decided by which Entropy Range slot holds each, not by the score.");
}
