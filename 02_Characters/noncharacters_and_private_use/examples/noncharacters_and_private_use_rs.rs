// A noncharacter is a scalar value, and Rust's type system says so out loud.
//
// The interesting thing about this half is what does NOT happen. `char` is the
// type that refuses a surrogate at construction, so a reader who has met it
// expects the same refusal here -- and gets `Some` sixty-six times. Nothing in
// `std` knows the word "noncharacter"; the range test at the top is the only
// definition on the machine.
//
// No reserved code point is printed as itself. Rust's Debug formatter escapes
// them anyway, which is section 5's whole point, and this file leans on that
// rather than working around it.

const RULE: &str = "------------------------------------------------------------------------";

/// The standard's two rules, and nothing else. There is no std equivalent.
fn is_noncharacter(cp: u32) -> bool {
    let low = cp & 0xFFFF;
    low == 0xFFFE || low == 0xFFFF || (0xFDD0..=0xFDEF).contains(&cp)
}

fn is_private_use(cp: u32) -> bool {
    (0xE000..=0xF8FF).contains(&cp)
        || (0xF0000..=0xFFFFD).contains(&cp)
        || (0x100000..=0x10FFFD).contains(&cp)
}

fn main() {
    println!("1. THE SAME TWO SETS, COUNTED BY A DIFFERENT LANGUAGE");
    println!("{RULE}");
    let noncharacters: Vec<u32> = (0..=0x10FFFF).filter(|&cp| is_noncharacter(cp)).collect();
    let private: Vec<u32> = (0..=0x10FFFF).filter(|&cp| is_private_use(cp)).collect();
    println!("   noncharacters   {}", noncharacters.len());
    println!("   private use     {}", private.len());
    println!("   the two sets are disjoint:  {}",
        !noncharacters.iter().any(|cp| is_private_use(*cp)));
    println!();
    println!("   Two programs, two languages, one sweep of the number line each,");
    println!("   and the same 66 and 137,468. Neither number was typed in.");
    println!();

    println!("2. char::from_u32 SAYS YES TO EVERY ONE OF THEM");
    println!("{RULE}");
    let built = noncharacters.iter().filter(|cp| char::from_u32(**cp).is_some()).count();
    println!("   noncharacters that char::from_u32 accepts:   {} of {}",
        built, noncharacters.len());
    let built_p = private.iter().filter(|cp| char::from_u32(**cp).is_some()).count();
    println!("   private-use code points it accepts:          {} of {}",
        built_p, private.len());
    println!();
    println!("   Which is worth pausing on, because `char` is the type that");
    println!("   REFUSES things. It is the strictest character type in this");
    println!("   library -- and it refuses exactly one class:");
    for cp in [0xD7FFu32, 0xD800, 0xDFFF, 0xE000, 0xFDD0, 0xFFFE, 0x10FFFF, 0x110000] {
        let note = if (0xD800..=0xDFFF).contains(&cp) {
            "a surrogate -- not a scalar value"
        } else if cp > 0x10FFFF {
            "past U+10FFFF -- not a code point"
        } else if is_noncharacter(cp) {
            "a NONCHARACTER, and still a scalar value"
        } else if is_private_use(cp) {
            "private use -- an ordinary scalar value"
        } else {
            "an ordinary scalar value"
        };
        println!("      {:26} {:5}  {}", format!("char::from_u32(0x{cp:X})"),
            if char::from_u32(cp).is_some() { "Some" } else { "None" }, note);
    }
    println!();
    println!("   Scalar value is the whole rule. `char` holds every code point");
    println!("   that is not a surrogate, and reservation is not part of the");
    println!("   contract -- so a noncharacter is as welcome in a String as an");
    println!("   'a' is. It also compiles as a LITERAL: '\\u{{FFFE}}' is accepted");
    println!("   by rustc with no lint and no warning.");
    println!();

    println!("3. AND SO DOES UTF-8, IN BOTH DIRECTIONS");
    println!("{RULE}");
    let mut round_tripped = 0usize;
    let mut buf = [0u8; 4];
    for &cp in &noncharacters {
        let ch = char::from_u32(cp).unwrap();
        let bytes = ch.encode_utf8(&mut buf).as_bytes().to_vec();
        if std::str::from_utf8(&bytes) == Ok(ch.to_string().as_str()) {
            round_tripped += 1;
        }
    }
    println!("   encoded to UTF-8 and validated back:  {} of {}",
        round_tripped, noncharacters.len());
    println!();
    println!("   str::from_utf8 is THE validator in this language -- the");
    println!("   boundary every &str is built behind -- and it has no objection:");
    for (bytes, label) in [
        (vec![0xEFu8, 0xBF, 0xBE], "U+FFFE, a noncharacter"),
        (vec![0xEFu8, 0xB7, 0x90], "U+FDD0, a noncharacter"),
        (vec![0xEEu8, 0x80, 0x80], "U+E000, private use"),
        (vec![0xEDu8, 0xA0, 0x80], "U+D800 spelled in UTF-8, a surrogate"),
    ] {
        let verdict = match std::str::from_utf8(&bytes) {
            Ok(_) => "Ok".to_string(),
            Err(e) => format!("Err at byte {}", e.valid_up_to()),
        };
        println!("      {:11}  {:16}  {}",
            bytes.iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" "),
            verdict, label);
    }
    println!();
    println!("   One of those four is rejected and it is not one of the reserved");
    println!("   ones. That is the page in a line.");
    println!();

    println!("4. NO PROPERTY, IN EITHER SET");
    println!("{RULE}");
    println!("   code point  alpha  ctrl   ws     upper  len_utf8  what it is");
    for (cp, what) in [
        (0x0041u32, "an ordinary letter"),
        (0xE000, "private use -- yours by agreement"),
        (0xF8FF, "private use -- Apple's logo, on Apple's machines"),
        (0xFDD0, "noncharacter -- nobody's, ever"),
        (0xFFFE, "noncharacter -- the BOM's mirror"),
        (0x0378, "unassigned -- may become a letter one day"),
    ] {
        let c = char::from_u32(cp).unwrap();
        println!("   U+{:<9} {:<6} {:<6} {:<6} {:<6} {:<9} {}",
            format!("{cp:04X}"), c.is_alphabetic(), c.is_control(),
            c.is_whitespace(), c.is_uppercase(), c.len_utf8(), what);
    }
    println!();
    println!("   Every column false on all four reserved rows -- and the same");
    println!("   five falses for the merely-unassigned U+0378. Rust cannot tell");
    println!("   you which is which either -- there is no is_noncharacter and no");
    println!("   is_private_use in std, which is why this file opens with two");
    println!("   range tests written by hand.");
    println!();

    println!("5. THE ONE PLACE RUST IS MORE HELPFUL THAN PYTHON");
    println!("{RULE}");
    println!("   Debug on a string holding one of each:");
    println!("      {:?}", format!("a{}b", char::from_u32(0xFFFE).unwrap()));
    println!("      {:?}", format!("a{}b", char::from_u32(0xE000).unwrap()));
    println!("      escape_unicode:  {}", char::from_u32(0xFFFE).unwrap().escape_unicode());
    println!();
    println!("   Debug escapes a non-printable scalar rather than emitting it, so");
    println!("   dbg! and a {{:?}} in a log show you the number. Display does not:");
    println!("   println!(\"{{}}\", c) writes the three raw bytes and your terminal");
    println!("   draws a box, or nothing, or whatever a font privately decided.");
    println!("   When you are hunting one of these, {{:?}} is the tool.");
    println!();

    println!("6. WHAT THEY ARE ACTUALLY FOR");
    println!("{RULE}");
    println!("   A sentinel has to be a value your input cannot contain. That is");
    println!("   the entire requirement, and it is why a noncharacter beats every");
    println!("   ASCII character somebody once picked for the job:");
    let text = "field one\u{FFFF}field two\u{FFFF}field three";
    println!("      joined on U+FFFF, then split:  {:?}",
        text.split('\u{FFFF}').collect::<Vec<_>>());
    println!("      pieces: {}", text.split('\u{FFFF}').count());
    println!();
    println!("   Nothing arriving from outside can contain U+FFFF, because no");
    println!("   conformant producer may emit it as text -- so unlike a comma, a");
    println!("   tab, a NUL or a pipe, this separator cannot be forged by the");
    println!("   data. Inside one process that is a real guarantee. The moment");
    println!("   the string leaves -- to a file, a socket, an XML document, a");
    println!("   filename -- the guarantee is gone and you have shipped a value");
    println!("   the standard says you must not interchange.");
}
