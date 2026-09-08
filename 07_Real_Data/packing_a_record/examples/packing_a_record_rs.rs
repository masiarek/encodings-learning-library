// The layout is in the method names, and there is no format string to get wrong.
//
// Rust has no `pack`. It has `to_be_bytes` and `to_le_bytes` on every integer
// and float, so a record is assembled a field at a time and the byte order is
// spelled out once per field rather than once per record. That is more typing
// and one fewer thing to leave off: there is no unsuffixed spelling, so there
// is no way to accidentally ask for "whatever this machine does".
//
// The other half of the contrast is what Rust will NOT let you do. A struct's
// in-memory layout is unspecified by default -- the compiler is free to reorder
// the fields -- so "just write the struct out" is not a thing you can express
// here at all. The wire record below is fourteen bytes because the code says
// fourteen bytes, not because the machine happened to lay it out that way.
//
// Sizes that belong to the machine are printed as comparisons rather than as
// numbers, for the reason `to_ne_bytes` is not printed on the byte-order page:
// a recorded answer key must not depend on who ran it.
//
// Build:  rustc --edition 2024 packing_a_record_rs.rs -o /tmp/pack && /tmp/pack

use std::mem::size_of;

/// One order line. In memory only -- nothing about this declaration is a
/// promise about bytes on a wire.
struct Order {
    id: u32,
    qty: i16,
    price: f64,
}

/// The same three fields, asking for C's layout rules: declaration order,
/// C's padding, C's alignment. Still a memory layout, still not a wire format.
#[repr(C)]
#[allow(dead_code)]
struct OrderC {
    id: u32,
    qty: i16,
    price: f64,
}

fn head(n: u32, title: &str) {
    println!("\n{n}. {title}\n{}", "-".repeat(72));
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect::<Vec<_>>().join(" ")
}

fn row(label: &str, bytes: &[u8], note: &str) {
    println!("   {label:<30} {:<50} {note}", hex(bytes));
}

fn main() {
    let order = Order { id: 4711, qty: -3, price: 19.5 };
    let name = "Zażółć";

    // -------------------------------------------------------------- 1
    head(1, "ONE METHOD CALL PER FIELD, AND THE ORDER IS IN THE NAME");

    let mut wire: Vec<u8> = Vec::new();
    wire.extend_from_slice(&order.id.to_be_bytes());
    wire.extend_from_slice(&order.qty.to_be_bytes());
    wire.extend_from_slice(&order.price.to_be_bytes());

    println!("   order.id.to_be_bytes()      {:<26} u32 -> 4 bytes", hex(&order.id.to_be_bytes()));
    println!("   order.qty.to_be_bytes()     {:<26} i16 -> 2 bytes", hex(&order.qty.to_be_bytes()));
    println!("   order.price.to_be_bytes()   {:<26} f64 -> 8 bytes", hex(&order.price.to_be_bytes()));
    println!();
    row("the three concatenated", &wire, &format!("{} bytes", wire.len()));
    println!();
    println!("   Those are the same fourteen bytes Python's struct.pack('>Ihd')");
    println!("   produces, which is the point: two languages, no shared code,");
    println!("   one agreed layout written down in two different places.");
    println!();
    println!("   There is no `to_bytes` without a suffix. `to_ne_bytes` exists");
    println!("   and is spelled out loud -- NATIVE endian -- so a program that");
    println!("   reaches for it has said so. The mistake Python's unprefixed");
    println!("   'Ihd' makes available by DEFAULT is, in Rust, six characters");
    println!("   you have to type on purpose.");

    // -------------------------------------------------------------- 2
    head(2, "THE STRUCT IN MEMORY IS NOT THE RECORD ON THE WIRE");

    println!("   size_of::<Order>()   -- not printed: the default layout is");
    println!("   size_of::<OrderC>()     UNSPECIFIED and repr(C)'s padding is");
    println!("                           the ABI's, so both are facts about");
    println!("                           this machine rather than about the");
    println!("                           record. What is a fact about the");
    println!("                           record is the line below.");
    println!();
    println!("   wire.len() == 4 + 2 + 8              {}", wire.len() == 14);
    println!("   wire.len() == size_of::<Order>()     {}", wire.len() == size_of::<Order>());
    println!("   wire.len() == size_of::<OrderC>()    {}", wire.len() == size_of::<OrderC>());
    println!();
    println!("   The two size_of lines are false, and for two different");
    println!("   reasons. repr(C) is larger than the sum of its fields because");
    println!("   the ABI pads an f64 up to its alignment -- eight bytes on");
    println!("   every 64-bit target in common use, and a number that belongs");
    println!("   to the target rather than to the language. The default");
    println!("   layout is whatever the compiler liked -- it may reorder the");
    println!("   fields, and the language promises nothing about the result");
    println!("   between two builds.");
    println!();
    println!("   So the C habit the C section of this page is about -- point");
    println!("   at the struct, write sizeof bytes, hope -- has no Rust");
    println!("   spelling. You cannot get the bytes of a struct without unsafe");
    println!("   code and an attribute, which is the language declining to let");
    println!("   a memory layout become a file format by accident.");

    // -------------------------------------------------------------- 3
    head(3, "READING BACK: THE WIDTH IS CHECKED, THE MEANING IS NOT");

    let id = u32::from_be_bytes(wire[0..4].try_into().unwrap());
    let qty = i16::from_be_bytes(wire[4..6].try_into().unwrap());
    let price = f64::from_be_bytes(wire[6..14].try_into().unwrap());
    println!("   read with from_be_bytes    id={id}  qty={qty}  price={price}");

    let wrong = u32::from_le_bytes(wire[0..4].try_into().unwrap());
    println!("   read with from_le_bytes    id={wrong}");
    println!();
    println!("   Same four bytes, two methods, two integers, no error. Rust");
    println!("   makes the byte order impossible to LEAVE OUT and no harder to");
    println!("   get wrong; nothing in those four bytes says which end goes");
    println!("   first, in any language.");
    println!();
    println!("   What the type system does catch is the width. `from_be_bytes`");
    println!("   takes [u8; 4] and not a slice, so a four-byte field read with");
    println!("   two bytes is a compile error -- see the page. From a slice the");
    println!("   same check happens at run time, and it is an error you can");
    println!("   handle rather than a truncation you cannot see:");
    println!();
    let short: Result<[u8; 4], _> = wire[0..2].try_into();
    let exact: Result<[u8; 4], _> = wire[0..4].try_into();
    println!("     <[u8; 4]>::try_from(&wire[0..2])   is_err: {}", short.is_err());
    println!("     <[u8; 4]>::try_from(&wire[0..4])   is_err: {}", exact.is_err());

    // -------------------------------------------------------------- 4
    head(4, "AND THE NAME FIELD, WHICH RUST HAS ALREADY DECIDED FOR YOU");

    let raw = name.as_bytes();
    println!("   let name = \"{name}\";");
    println!("     name.chars().count()   {}   characters", name.chars().count());
    println!("     name.len()             {}  bytes -- len() on a str is BYTES", raw.len());
    println!("     name.as_bytes()        {}", hex(raw));
    println!();
    println!("   `as_bytes` costs nothing and takes no encoding argument,");
    println!("   because a Rust `str` is UTF-8 by definition -- the decision");
    println!("   Python's struct.pack('10s', ...) refuses to make for you was");
    println!("   made when the string was constructed. That removes one of the");
    println!("   four decisions and none of the other three.");
    println!();
    println!("   The byte budget is still yours, and the cut is still a cut:");
    println!();
    for candidate in ["Adam", "Zażółć", "Zażółći"] {
        println!("     {:<8} {} chars {:>3} bytes   fits a 10-byte field: {}",
                 candidate, candidate.chars().count(), candidate.len(),
                 candidate.len() <= 10);
    }
    println!();
    println!("   And where Python hands you nine bytes and finds out later,");
    println!("   Rust will not build a `str` out of a cut sequence at all:");
    println!();
    let nine = &raw[..9];
    println!("     &name.as_bytes()[..9]           {}", hex(nine));
    println!("     str::from_utf8(that)  is_err:   {}", std::str::from_utf8(nine).is_err());
    println!("     name.is_char_boundary(9)        {}", name.is_char_boundary(9));
    println!("     name.is_char_boundary(8)        {}", name.is_char_boundary(8));
    println!();
    println!("   `is_char_boundary` is the question a byte budget actually");
    println!("   asks, and it is on `str` in std rather than in a crate. Byte 9");
    println!("   is inside the two bytes that spell the last letter; byte 8 is");
    println!("   between characters. Slicing a `str` at 9 panics rather than");
    println!("   returning half a character -- loud where Python's '9s' is");
    println!("   silent.");

    // -------------------------------------------------------------- 5
    head(5, "THE WHOLE RECORD, WITH THE NAME IN IT");

    let mut full: Vec<u8> = Vec::new();
    full.extend_from_slice(&order.id.to_be_bytes());
    full.extend_from_slice(&order.qty.to_be_bytes());
    let mut field = [0u8; 10];               // NUL-padded, like '10s'
    assert!(raw.len() <= field.len(), "name does not fit the field");
    field[..raw.len()].copy_from_slice(raw);
    full.extend_from_slice(&field);

    row("id + qty + 10-byte name", &full, &format!("{} bytes", full.len()));
    println!();
    let back_id = u32::from_be_bytes(full[0..4].try_into().unwrap());
    let back_qty = i16::from_be_bytes(full[4..6].try_into().unwrap());
    let back_name = std::str::from_utf8(&full[6..16]).unwrap().trim_end_matches('\0');
    println!("   read back      id={back_id}  qty={back_qty}  name={back_name:?}");
    println!("   round trips:   {}",
             back_id == order.id && back_qty == order.qty && back_name == name);
    println!();
    println!("   The `assert!` above is the whole difference from section 6 of");
    println!("   the Python run. Nothing in the language forces it -- a fixed");
    println!("   array and a `copy_from_slice` panic on an over-long name");
    println!("   rather than truncating, which is better than silence and");
    println!("   worse than a checked error at the edge of the system. The");
    println!("   width of a field is the one part of a binary layout that no");
    println!("   type can hold.");
    println!();
}
