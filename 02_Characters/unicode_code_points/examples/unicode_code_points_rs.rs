//! `char` is exactly one code point, and the type says so.
//!
//! Python will hold a lone surrogate in a `str` and only complain when you
//! ask for bytes. Rust refuses one character earlier: `char::from_u32`
//! returns `None`, so the gap in the number line is enforced by the type
//! rather than by a later encode step.
//!
//! The last section is the neighbourhood map, measured rather than quoted:
//! every code point Unicode calls whitespace, printed as the runs it
//! actually forms. Ten runs, and knowing where they are beats knowing them.
//!
//! Run:  rustc --edition 2024 unicode_code_points_rs.rs && ./unicode_code_points_rs

const BAR: &str = "------------------------------------------------------------------------";

fn head(n: u32, title: &str) {
    println!("\n{n}. {title}\n{BAR}");
}

fn main() {
    head(1, "A char IS A CODE POINT, AND from_u32 IS THE GATE");
    for cp in [0x41u32, 0xE9, 0x104, 0x20AC, 0x1F600, 0xD800, 0x110000] {
        let addr = format!("U+{cp:04X}");
        match char::from_u32(cp) {
            Some(c) => println!("   {addr:<10}Some({c:?})"),
            None => println!("   {addr:<10}None   <- not a scalar value"),
        }
    }
    println!();
    println!("   The last two are the only two ways to fail: a surrogate,");
    println!("   and anything past the top of the number line.");

    head(2, "THE HOLE IN THE MIDDLE: U+D800..=U+DFFF");
    let surrogates = (0xD800u32..=0xDFFF).filter(|&c| char::from_u32(c).is_none()).count();
    println!("   code points in that range rejected by char: {surrogates}");
    println!("   they exist only so UTF-16 can spell the upper planes,");
    println!("   which is why they are reserved and never characters.");

    head(3, "THE COUNT IS DEFINITIONAL, NOT A TABLE LOOKUP");
    let total = 0x110000u32;
    println!("   0x110000            = {total:>9}   17 planes of 65,536");
    println!("   minus the surrogates= {:>9}", surrogates);
    println!("   usable scalars      = {:>9}", total - surrogates as u32);
    println!();
    println!("   and every one of them fits in a char, which is always");
    println!("   {} bytes wide -- a code point, not a UTF-8 byte.", size_of::<char>());

    head(4, "WRITING ONE DOWN IN SOURCE");
    let e = '\u{E9}';
    println!("   '\\u{{E9}}' is {e:?}, and as a number {}", e as u32);
    println!("   escape_unicode goes the other way: {}", 'Ą'.escape_unicode());
    println!("   a char knows its own neighbourhood by arithmetic:");
    println!("      is_ascii()      {}", e.is_ascii());
    println!("      is_alphabetic() {}", e.is_alphabetic());
    println!("      len_utf8()      {}   <- chapter 3's question", e.len_utf8());

    head(5, "THE NEIGHBOURHOOD MAP, MEASURED: WHERE WHITESPACE LIVES");
    let mut runs: Vec<(u32, u32)> = Vec::new();
    for cp in 0u32..=0x10FFFF {
        if char::from_u32(cp).is_some_and(char::is_whitespace) {
            match runs.last_mut() {
                Some(r) if r.1 + 1 == cp => r.1 = cp,
                _ => runs.push((cp, cp)),
            }
        }
    }
    let total_ws: u32 = runs.iter().map(|(a, b)| b - a + 1).sum();
    println!("   {total_ws} code points, in {} runs -- not 25 things to learn:", runs.len());
    println!();
    for (a, b) in &runs {
        let span = if a == b {
            format!("U+{a:04X}")
        } else {
            format!("U+{a:04X}..=U+{b:04X}")
        };
        let gloss = match a {
            0x0009 => "TAB LF VT FF CR -- the run 9-A-B-C-D",
            0x0020 => "SPACE, the first printable code point",
            0x0085 => "NEL, over in the C1 controls (0080-009F)",
            0x00A0 => "NO-BREAK SPACE = 0x20 | 0x80",
            0x1680 => "OGHAM SPACE MARK, first slot of its block",
            0x2000 => "the printer's type case: quads down to a hair",
            0x2028 => "LINE then PARAGRAPH separator, smaller first",
            0x202F => "NARROW NO-BREAK SPACE",
            0x205F => "MEDIUM MATHEMATICAL SPACE",
            0x3000 => "IDEOGRAPHIC SPACE, where the CJK zone opens",
            _ => "",
        };
        println!("   {span:<19} {gloss}");
    }
    println!();
    println!("   Four neighbourhoods carry all of it: the ASCII controls,");
    println!("   Latin-1's high half, the 2000 punctuation block, and CJK.");
    println!();
    println!("   The two exceptions both end in B, and both are traps:");
    for cp in [0x000Bu32, 0x200B] {
        let c = char::from_u32(cp).unwrap();
        println!(
            "      U+{cp:04X}  is_whitespace {:<5} is_ascii_whitespace {}",
            c.is_whitespace(),
            c.is_ascii_whitespace()
        );
    }
    println!("   U+000B VERTICAL TAB is whitespace but not ASCII whitespace.");
    println!("   U+200B ZERO WIDTH SPACE is named a space and is neither.");
}
