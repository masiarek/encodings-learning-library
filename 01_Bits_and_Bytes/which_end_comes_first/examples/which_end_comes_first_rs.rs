// Rust has no `to_bytes`. The order is in the method NAME, so there is nothing
// to leave out and nothing to default.
//
// Run:  rustc --edition 2024 which_end_comes_first_rs.rs && ./which_end_comes_first_rs

fn main() {
    let n: u32 = 0x002F_7505;

    println!("1. THREE METHODS, NO FLAG");
    println!("   n = 0x{n:08x}  ({n})");
    println!("   n.to_be_bytes()   {:02x?}", n.to_be_bytes());
    println!("   n.to_le_bytes()   {:02x?}", n.to_le_bytes());
    println!("   n.to_ne_bytes()   {:02x?}", n.to_ne_bytes());
    println!("   There is no n.to_bytes(). You cannot decline to choose, because");
    println!("   the choice is spelled into the name you call -- which also means");
    println!("   `grep to_ne_bytes` finds every place a program committed to the");
    println!("   machine it was built on. The Python version of that mistake is a");
    println!("   call with the argument LEFT OUT, and no grep finds a missing word.");

    println!();
    println!("2. WHAT THIS BUILD TARGETS");
    println!("   cfg!(target_endian = \"little\")   {}", cfg!(target_endian = "little"));
    println!("   cfg!(target_endian = \"big\")      {}", cfg!(target_endian = "big"));
    println!("   `ne` is whichever of those is true, decided at COMPILE time, so a");
    println!("   cross-compiled binary and the machine that built it can disagree.");

    println!();
    println!("3. THE WIDTH IS IN THE TYPE");
    let bytes: [u8; 4] = [0x00, 0x2f, 0x75, 0x05];
    println!("   bytes                          {bytes:02x?}");
    println!("   u32::from_be_bytes(bytes)      {}", u32::from_be_bytes(bytes));
    println!("   u32::from_le_bytes(bytes)      {}", u32::from_le_bytes(bytes));
    println!("   from_be_bytes takes [u8; 4], not &[u8]: a slice of the wrong");
    println!("   length is a compile error, not a runtime surprise. Python's");
    println!("   int.from_bytes accepts any length and quietly means it.");

    println!();
    println!("4. THE SAME MISMATCH AS EVERY OTHER LANGUAGE");
    let written = n.to_le_bytes();
    let misread = u32::from_be_bytes(written);
    println!("   wrote {n} little-endian   -> {written:02x?}");
    println!("   read it back big-endian       -> {misread}");
    println!("   Rust makes you NAME the order; it cannot make you name the same");
    println!("   one twice. Nothing here is unsafe, nothing panics, and the number");
    println!("   is simply wrong -- the compiler was never told the two calls were");
    println!("   supposed to agree.");
}
