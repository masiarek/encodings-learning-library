// Rust asks the same question and gets a different answer, because its table is
// not on the machine at all -- rustc compiled it into this binary.

fn rule() {
    println!("{}", "-".repeat(72));
}

// The version is a const, so the compiler can reason about it. If it were read
// from the host at run time, this line could not compile.
const _: () = assert!(char::UNICODE_VERSION.0 >= 9);

fn main() {
    println!("1. THE TABLE TRAVELS WITH THE BINARY");
    rule();
    println!("   char::UNICODE_VERSION is a (u8, u8, u8) const, baked in by rustc.");
    println!("   Its value is not printed here, for the reason the Python program");
    println!("   gives: it is a fact about the toolchain that built this file, not");
    println!("   a fact about Unicode.");
    println!();
    println!("   is it at least 9.0?   {}", char::UNICODE_VERSION.0 >= 9);
    println!("   ...and the compiler agreed before the program ever ran:");
    println!("      const _: () = assert!(char::UNICODE_VERSION.0 >= 9);");
    println!();
    println!("   That const assert is the whole difference from Python. Python");
    println!("   reads unicodedata at run time, so the answer follows whichever");
    println!("   interpreter you launch. Rust settles it at compile time, so a");
    println!("   binary keeps the table its rustc had. Two machines running the");
    println!("   SAME binary can never disagree; two machines compiling the same");
    println!("   source very well can.");
    println!();

    println!("2. DEFINITIONAL HERE TOO, AND STILL FREE OF THE TABLE");
    rule();
    println!("   char::MAX                        U+{:04X}", char::MAX as u32);
    println!("   char::from_u32(0xD800)           {:?}   <- the surrogate hole", char::from_u32(0xD800));
    println!("   char::from_u32(0x110000)         {:?}   <- past the end", char::from_u32(0x110000));
    println!("   usable scalar values             {}", 0x110000u32 - 2048);
    println!();
    println!("   None of those four consult a table. They are the shape of the");
    println!("   number line, fixed when UTF-16 fixed it, and no Unicode release");
    println!("   can move them.");
    println!();

    println!("3. THESE DO CONSULT IT -- AND THESE ANSWERS ARE STILL SAFE");
    rule();
    println!("   code point  alphabetic  uppercase  len_utf8   char");
    for c in ['é', '\u{1E9E}', '😀', '\u{FFFE}'] {
        println!(
            "   {:<12}{:<12}{:<11}{:<11}{}",
            format!("U+{:04X}", c as u32),
            c.is_alphabetic(),
            c.is_uppercase(),
            c.len_utf8(),
            c
        );
    }
    println!();
    println!("   The first three have been settled since 2010 at the latest, and");
    println!("   General_Category is not a property Unicode changes lightly -- but");
    println!("   note that it is NOT on the stability list, so `settled` here means");
    println!("   observed, not promised. The fourth row is the promised one:");
    println!("   U+FFFE is a PERMANENT noncharacter, guaranteed never to be assigned");
    println!("   anything, so `false` there is not a reading of today's table but a");
    println!("   statement about every future one. That is the kind of lookup that");
    println!("   can safely go in a test.");
    println!();

    println!("4. AND THE ONE THIS PROGRAM REFUSES TO ANSWER");
    rule();
    println!("   U+11DB0 TOLONG SIKI LETTER I arrived in Unicode 17.0, in September");
    println!("   2025. A rustc built before that says `false`; one built after says");
    println!("   `true`. Same source, same machine, same input, and no bug -- so the");
    println!("   row is described here and not printed. Ask your own compiler:");
    println!();
    println!("       fn main() {{ println!(\"{{}}\", '\\u{{11DB0}}'.is_alphabetic()); }}");
    println!();
    println!("   Then ask the python3 next to it. On the machine this page was");
    println!("   written on the two did not agree, and the page says so in a fence");
    println!("   with a date on it, because that is the only honest place for it.");
    println!();

    println!("5. ONE MORE THE TABLE DECIDES FOR YOU");
    rule();
    let ss: String = 'ß'.to_uppercase().collect();
    println!("   'ß'.to_uppercase()               {:?}   ({} chars)", ss, ss.chars().count());
    println!("   U+1E9E exists as a single char   {:?}", char::from_u32(0x1E9E));
    println!();
    println!("   Uppercasing ß gives two characters, not the single one that has");
    println!("   existed since 2008. That is not arithmetic and not an oversight --");
    println!("   it is a line in SpecialCasing.txt, which is to say a row in the");
    println!("   table, which is to say something that has a version.");
}
